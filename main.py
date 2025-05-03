#!/usr/bin/env python3
"""
Command Line Interface for database management in the educational institution system.

This module provides a CLI for performing CRUD operations on the database entities
including Groups, Students, Teachers, Subjects, and Grades.
"""

import argparse
import sys
from typing import Any, Dict, List, Type, Optional, Union

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import DeclarativeMeta

from models import Group, Student, Teacher, Subject, Grade, Base
from db_config import DATABASE_URL


ModelType = Type[Union[Group, Student, Teacher, Subject, Grade]]
ModelsDict = Dict[str, ModelType]


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Create and return a new database session."""
        return self.Session()


class RecordManager:
    """Handles database CRUD operations for model entities."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, model: ModelType, **kwargs: Any) -> None:
        """Create a new record in the database."""
        try:
            record = model(**kwargs)
            self.session.add(record)
            self.session.commit()
            print(f"Created {model.__name__}: {kwargs}")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error creating {model.__name__}: {e}")
    
    def list_all(self, model: ModelType) -> None:
        """List all records of a model."""
        try:
            records = self.session.query(model).all()
            if not records:
                print(f"No {model.__name__} records found.")
                return
                
            for record in records:
                record_dict = {k: v for k, v in record.__dict__.items() if not k.startswith('_')}
                print(record_dict)
        except SQLAlchemyError as e:
            print(f"Error listing {model.__name__} records: {e}")
    
    def update(self, model: ModelType, record_id: int, **kwargs: Any) -> None:
        """Update an existing record by ID."""
        try:
            record = self.session.query(model).filter_by(id=record_id).first()
            if record:
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                self.session.commit()
                print(f"Updated {model.__name__} with ID {record_id}: {kwargs}")
            else:
                print(f"{model.__name__} with ID {record_id} not found.")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error updating {model.__name__} with ID {record_id}: {e}")
    
    def delete(self, model: ModelType, record_id: int) -> None:
        """Delete a record by ID."""
        try:
            record = self.session.query(model).filter_by(id=record_id).first()
            if record:
                self.session.delete(record)
                self.session.commit()
                print(f"Deleted {model.__name__} with ID {record_id}")
            else:
                print(f"{model.__name__} with ID {record_id} not found.")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error deleting {model.__name__} with ID {record_id}: {e}")


class CommandLineInterface:
    """CLI for interacting with database models."""
    
    MODELS: ModelsDict = {
        "Group": Group,
        "Student": Student,
        "Teacher": Teacher,
        "Subject": Subject,
        "Grade": Grade,
    }
    
    def __init__(self, record_manager: RecordManager):
        self.record_manager = record_manager
    
    def setup_argument_parser(self) -> argparse.ArgumentParser:
        """Configure and return the argument parser."""
        parser = argparse.ArgumentParser(
            description="CLI for CRUD operations on the educational institution database."
        )
        parser.add_argument(
            "-a",
            "--action",
            required=True,
            choices=["create", "list", "update", "remove"],
            help="Action to perform",
        )
        parser.add_argument(
            "-m",
            "--model",
            required=True,
            choices=list(self.MODELS.keys()),
            help="Model to operate on",
        )
        parser.add_argument("--id", type=int, help="ID of the record (for update/remove)")
        parser.add_argument("--name", help="Name of the record (for create/update)")
        parser.add_argument("--group_id", type=int, help="Group ID (for Student)")
        parser.add_argument("--teacher_id", type=int, help="Teacher ID (for Subject)")
        parser.add_argument("--student_id", type=int, help="Student ID (for Grade)")
        parser.add_argument("--subject_id", type=int, help="Subject ID (for Grade)")
        parser.add_argument("--grade", type=float, help="Grade value (for Grade)")
        return parser
    
    @staticmethod
    def collect_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
        """Collect keyword arguments from command line arguments."""
        kwargs = {}
        if args.name is not None:
            kwargs["name"] = args.name
        if args.group_id is not None:
            kwargs["group_id"] = args.group_id
        if args.teacher_id is not None:
            kwargs["teacher_id"] = args.teacher_id
        if args.student_id is not None:
            kwargs["student_id"] = args.student_id
        if args.subject_id is not None:
            kwargs["subject_id"] = args.subject_id
        if args.grade is not None:
            kwargs["grade"] = args.grade
        return kwargs
    
    def process_args(self, args: argparse.Namespace) -> None:
        """Process command line arguments and execute corresponding action."""
        try:
            model = self.MODELS[args.model]
            
            if args.action == "create":
                kwargs = self.collect_kwargs(args)
                if not kwargs:
                    print("Error: No attributes provided for create action.")
                    return
                self.record_manager.create(model, **kwargs)
                
            elif args.action == "list":
                self.record_manager.list_all(model)
                
            elif args.action == "update":
                if not args.id:
                    print("Error: --id is required for update action.")
                    return
                kwargs = self.collect_kwargs(args)
                if not kwargs:
                    print("Error: No attributes provided for update action.")
                    return
                self.record_manager.update(model, args.id, **kwargs)
                
            elif args.action == "remove":
                if not args.id:
                    print("Error: --id is required for remove action.")
                    return
                self.record_manager.delete(model, args.id)
                
        except KeyError:
            print(f"Error: Unknown model '{args.model}'")
        except Exception as e:
            print(f"Error: {e}")


def main() -> None:
    """Main function to handle CLI arguments and dispatch appropriate actions."""
    try:
        # Initialize database connection
        db_manager = DatabaseManager(DATABASE_URL)
        session = db_manager.get_session()
        
        # Initialize record manager with session
        record_manager = RecordManager(session)
        
        # Initialize CLI with record manager
        cli = CommandLineInterface(record_manager)
        
        # Parse command line arguments
        parser = cli.setup_argument_parser()
        args = parser.parse_args()
        
        # Process arguments and execute action
        cli.process_args(args)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    finally:
        if 'session' in locals():
            session.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
