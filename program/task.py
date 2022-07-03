""" 
This is where all Todo_list and Task properties will be defined 
"""

class Todo_list:
    """
    Storage for tasks.
    A Todo_list must have the ff:
    - a UNIQUE name,
    - a creation_date,
    A Todo_list can have an empty amount of tasks.
    """
    def __init__(self, name: str, creation_date: str) -> None:
        self.name = name
        self.creation_date = creation_date
        self.tasks = []
        
    def Todo_list_details(self) -> str:
        """
        Shows Todo_list details in a particular format
        """
        return f"Todo_list Name: {self.name}, Made in: {self.creation_date}"


class Task(Todo_list):
    """
    A child of Todo_list,
    A Task must have the ff:
    - a ParentList, or which Todo_list it belongs to,
    - a name,
    - a creation_date,
    - a date deadline (mm/dd/yy),
    - a time deadline (hh/mm/am_pm)

    The completion state of the of a Task is always set to False unless toggled.
    """
    def __init__(self, parent: str, name: str, creation_date: str, deadline_date: str, deadline_time: str) -> None:
        self.parent = parent
        self.name = name
        self.creation_date = creation_date
        self.deadline_date = deadline_date
        self.deadline_time = deadline_time
        self.is_completed = False

    def details(self) -> str:
        return f"Task Name: {self.name} Made in: {self.creation_date}, Deadline in: {self.date_deadline} at: {self.time_deadline}"
