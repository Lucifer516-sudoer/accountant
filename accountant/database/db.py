"""
Contains a class for managing financial transactions stored in a CSV file.
"""

# TODO: Add documentation later
# * Now Focus on the core stuff

import logging
from csv import DictReader, DictWriter
from decimal import Decimal
from pathlib import Path
from typing import Any

from accountant.database.entry import Entry, FlowType

from pydantic import BaseModel

from accountant.logging import app_logger


class UpdateCondition(BaseModel):
    """
    The Condition that is given when there is a need for an update.
    Similar to `UPDATE where VALUE = SOME_VALUE with NEW_VALUE`
    """

    where: str
    value: Any
    with_new_value: Any

    def __str__(self) -> str:
        return f"WHERE::{self.where} == VALUE::{self.value} THEN UPDATE WITH::{self.with_new_value}"

    def __repr__(self) -> str:
        return self.__str__()


class Query(BaseModel):
    """
    Simple query statement
    """

    where: str
    value: Any

    def __str__(self) -> str:
        return f"WHERE::{self.where} == VALUE::{self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class CSVDataBase:
    """
    CSVDataBase - A class for managing financial transactions stored in a CSV file.

    This class provides methods to perform CRUD (Create, Read, Update, Delete) operations
    on financial entries stored in a CSV file. It supports writing new entries, reading all entries,
    querying entries based on conditions, updating existing entries, and deleting entries.

    Attributes:
        path (Path): Path to the CSV file storing financial entries.
        _reader (type): Reader type for reading CSV data.
        _writer (type): Writer type for writing CSV data.
        field_names (list[str]): Field names for the CSV file representing attributes of Entry.

    Methods:
        __init__(path: Path) -> None:
            Initializes the CSVDataBase instance with the given file path.

        read_all(*, return_as: type[Entry] = Entry) -> list[Entry] | None:
            Reads all entries from the CSV file and returns them as a list of Entry objects.

        write(entries: list[Entry]) -> Path:
            Writes a list of Entry objects to the CSV file.

        get_by(query: Query) -> list[Entry] | None:
            Retrieves entries from the CSV file based on the specified query condition.

        update(condition: UpdateCondition) -> None:
            Updates entries in the CSV file based on the specified update condition.

        delete(condition: Query | Entry) -> None:
            Deletes entries from the CSV file based on the specified query or entry instance.
    """

    logger = app_logger.getChild("db")

    def __init__(self, path: Path) -> None:
        """
        Initialize the CSVDataBase instance.

        Args:
            path (Path): Path to the CSV file storing financial entries.
        """
        self.path = path
        self._reader = DictReader
        self._writer = DictWriter
        # self.field_names = [
        #     "date_time",
        #     "name",
        #     "amount",
        #     "reason",
        #     "tag",
        #     "flow_type",
        # ]

        self.field_names: list[str] = list(Entry.model_fields.keys())
        self.logger.info("Initialized CSV DataBase Class")
        self.logger.debug("Config:")
        self.logger.debug(f"CSV File Path       : {self.path}")
        self.logger.debug(f"Allowed Field Names : {self.field_names}")

    #
    # Internal Functions
    # ! Need not be exposed
    #

    def __does_csv_file_exist(self):
        """
        Checks if the CSV file path given is a file and if it also exists
        """

        self.logger.info("Checking for the existence of the file")
        if self.path.is_file() and self.path.exists():
            self.logger.debug("CSV File Exists")
            return True
        else:
            self.logger.debug("CSV File Does not Exist")
            return False

    def read_all(self, *, return_as: type[Entry] = Entry) -> list[Entry] | None:
        """
        Read all entries from the CSV file.

        Args:
            return_as (type[Entry], optional): Type to convert each entry. Defaults to Entry.

        Returns:
            list[Entry] | None: List of Entry objects read from the CSV file, or None if the file is empty.
        """
        self.logger.info("Reading Data from CSV file")
        if self.__does_csv_file_exist():  # Reads, everything and returns it
            with open(self.path, newline="") as file:
                data = [Entry(**each) for each in list(self._reader(file))]  # type: ignore
                self.logger.info(f"Read {len(data)} entries from the CSV file.")
                return data
        else:
            self.logger.error(f"File: {self.path} does not exist. Cannot read data.")
            raise FileNotFoundError(self.path)

    def write(self, entries: list[Entry]) -> bool:
        """
        Write a list of Entry objects to the CSV file.

        Args:
            entries (list[Entry]): List of Entry objects to write.

        Returns:
            Bool: `True` if written successfully without exceptions, else `False`
        """
        try:
            with open(self.path, "a+", newline="") as file:
                writer = self._writer(file, fieldnames=self.field_names)

                # Yah this essentially checks the size of the file I guess
                if self.path.stat().st_size == 0:
                    # Writes header with the field names
                    self.logger.info("Adding Header field names")
                    self.logger.debug(
                        "The Size of the CSV File is typically zero, which means the header needs to be added"
                    )
                    self.logger.debug(f"Header Field names: {self.field_names}")
                    writer.writeheader()

                writer.writerows([each.model_dump() for each in entries])

            self.logger.info(
                f"Successfully wrote {len(entries)} entries to the CSV file."
            )
            return True
        except Exception as err:
            self.logger.exception(f"{err}: Failed to write entries to the CSV file.")
            return False

    def get_by(self, query: Query) -> list[Entry] | None:
        """
        Retrieve entries from the CSV file based on the specified query condition.

        Args:
            query (Query): Query object specifying the condition for retrieval.

        Returns:
            list[Entry] | None: List of Entry objects matching the query condition, or None if no matches.
        """
        self.logger.info(f"Querying entries with condition: {query}")
        try:
            data = self.read_all()
            if data:
                filtered_data: list[Entry] = []
                for each in data:
                    if (
                        hasattr(each, query.where)
                        and getattr(each, query.where) == query.value
                    ):
                        filtered_data.append(each)
                self.logger.info(
                    f"Found {len(filtered_data)} entries matching the query."
                )
                return filtered_data
            else:
                self.logger.info("No data found in the CSV file.")
                return None
        except Exception as err:
            self.logger.exception(f"{err}: Error Encountered during Update Operation")
            return None

    def update(self, condition: UpdateCondition):
        """
        Update entries in the CSV file based on the specified update condition.

        Args:
            condition (UpdateCondition): UpdateCondition object specifying the update condition.
        """
        self.logger.info(f"Updating entries with condition: {condition}")
        data = self.read_all()
        try:
            if data:
                for each in data:
                    if (
                        hasattr(each, condition.where)
                        and getattr(each, condition.where) == condition.value
                    ):
                        setattr(each, condition.where, condition.with_new_value)
                self.write(data)
                self.logger.info("Update operation completed.")
                return True
            else:
                self.logger.info("No data found to update.")
                return False
        except Exception as err:
            self.logger.exception(f"{err}: Error Encountered during Update Operation")
            return False

    def delete(self, condition: Query | Entry) -> bool:
        """
        Delete entries from the CSV file based on the specified query or entry instance.

        Args:
            condition (Query | Entry): Query object specifying condition or Entry instance to delete.
        """
        self.logger.info(f"Deleting entries with condition: {condition}")
        if self.__does_csv_file_exist():
            temp_file = self.path.with_suffix(
                ".temp-to-re-write.csv"
            )  # yah might throw up error, if there is an file like this already in the system
            with open(self.path, "r", newline="") as read_file, open(
                temp_file, "w", newline=""
            ) as write_file:
                self.logger.debug(f"Opened temporary file: {temp_file}")
                reader = self._reader(read_file)
                writer = self._writer(write_file, fieldnames=self.field_names)

                writer.writeheader()

                deleted_count = 0
                for row in reader:
                    entry = Entry(
                        **row  # type: ignore
                    )  # Assuming Entry can be initialized from a dict

                    if isinstance(condition, Query):
                        # Check the condition and skip writing this row if it matches the condition
                        if getattr(entry, condition.where) == condition.value:
                            deleted_count += 1
                            continue

                    elif isinstance(condition, Entry):
                        # Check if the entry matches and skip writing this row if it matches the condition
                        if entry.id == condition.id:  # Compare by ID for exact match
                            deleted_count += 1
                            continue
                    # Write the row to the temp file if it doesn't match the delete condition
                    writer.writerow(row)

            # Replace the original file with the temp file after successful deletion
            temp_file.replace(self.path)
            self.logger.info(f"Deleted {deleted_count} entries from the CSV file.")
            return True
        else:
            self.logger.error("CSV file does not exist for deleting.")
            return False


if __name__ == "__main__":
    from time import perf_counter
    from rich import print
    from rich.traceback import install

    install(show_locals=True)

    # Create some dummy entries
    dummy = Entry(name="Usr", amount=Decimal(123123123), reason="JFF")
    dummy2 = Entry(
        name="Usr", amount=Decimal(123123123), reason="JFF", flow_type=FlowType.SAVINGS
    )
    dummy3 = Entry(
        name="Spcl", amount=Decimal(123123123), reason="JFF", flow_type=FlowType.SAVINGS
    )

    size = 1_000_000  # Example size of entries, which at 10 entries/day won't get to this much size
    db = CSVDataBase(Path("test-db.csv"))

    # Measure write performance
    write_st = perf_counter()
    db.write([dummy, dummy2, dummy3] * size)
    write_stp = perf_counter()

    # Measure read performance
    read_st = perf_counter()
    read_data = db.read_all()
    print(read_data)
    print(f"Read {len(read_data)} number of datum.")  # type: ignore
    read_stp = perf_counter()

    # Measure search performance
    search_st = perf_counter()
    data = db.get_by(Query(where="flow_type", value=FlowType.SAVINGS))
    search_stp = perf_counter()
    print("Searched and filtered data size:", len(data))  # type: ignore

    # Measure update performance
    update_st = perf_counter()
    db.update(UpdateCondition(where="name", value="Spcl", with_new_value="Not SO Spcl"))
    update_stp = perf_counter()

    # Measure delete performance
    delete_st = perf_counter()
    db.delete(Query(where="name", value="Usr"))
    delete_stp = perf_counter()

    print("-" * 20)
    print(f"""Written Dummy Data Size : {size} ✖️ 4
Read Time               : {read_stp-read_st:.4f} seconds
Write Time              : {write_stp-write_st:.4f} seconds
Search By Time          : {search_stp-search_st:.4f} seconds
Update Time             : {update_stp-update_st:.4f} seconds
Delete Time             : {delete_stp-delete_st:.4f} seconds
""")
