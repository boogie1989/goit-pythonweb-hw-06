from argparse import ArgumentParser
from connect import session
from models import Student, Group, Subject, Grade, Teacher

ACTIONS = {
    "create": "create",
    "list": "list",
    "remove": "remove",
    "update": "update",
}
MODELS_MAPPER = {
    "Student": Student,
    "Group": Group,
    "Subject": Subject,
    "Grade": Grade,
    "Teacher": Teacher,
}

ARGUMENTS_BY_MODEL = {
    ACTIONS["create"]: {
        Teacher: {"required": ["name"], "optional": []},
        Student: {"required": ["name", "group_id"], "optional": []},
        Subject: {"required": ["name", "teacher_id"], "optional": []},
        Group: {"required": ["name"], "optional": []},
        Grade: {
            "required": ["student_id", "subject_id", "grade", "date"],
            "optional": [],
        },
    },
    ACTIONS["remove"]: {
        Teacher: {"required": ["id"], "optional": []},
        Student: {"required": ["id"], "optional": []},
        Subject: {"required": ["id"], "optional": []},
        Group: {"required": ["id"], "optional": []},
        Grade: {"required": ["id"], "optional": []},
    },
    ACTIONS["update"]: {
        Teacher: {"required": ["id"], "optional": ["name"]},
        Student: {
            "required": ["id"],
            "optional": ["name", "group_id"],
        },
        Subject: {
            "required": ["id"],
            "optional": ["name", "teacher_id"],
        },
        Group: {
            "required": ["id"],
            "optional": ["name"],
        },
        Grade: {
            "required": ["id"],
            "optional": ["student_id", "subject_id", "grade", "date"],
        },
    },
}


def validate(default_fields, params):
    required = default_fields["required"]
    optional = default_fields["optional"]
    fields = {}

    for key, value in params.items():
        if value:
            if key in required or key in optional:
                fields[key] = value

    diff_required = list(set(required) - set(fields.keys()))
    if len(diff_required) > 0:
        raise ValueError(
            f"[!] Не вистачає обов'язкових даних для продовження: {diff_required}. Опціональні дані: {optional}"
        )

    return fields


def list_action(Model, **params):
    query = session.query("*").select_from(Model)

    if params["id"]:
        query = query.filter(Model.id == params["id"])
    if params["limit"]:
        query = query.limit(params["limit"])

    result = query.all()
    session.close()
    return result


def execute_action(action, Model, params):
    default_args = ARGUMENTS_BY_MODEL[action][Model]
    fields = validate(default_args, params)

    if action == ACTIONS["create"]:
        session.add(Model(**fields))
    elif action == ACTIONS["update"]:
        session.query(Model).filter(Model.id == params["id"]).update(fields)
    elif action == ACTIONS["remove"]:
        session.query(Model).filter(Model.id == params["id"]).delete()

    session.commit()
    session.close()


def main():
    parser = ArgumentParser(description="Select from database")
    parser.add_argument(
        "-a",
        "--action",
        choices=ACTIONS.values(),
        type=str,
        required=True,
    )
    parser.add_argument(
        "-m",
        "--model",
        choices=["Student", "Group", "Teacher", "Subject", "Grade"],
        type=str,
        required=True,
    )

    parser.add_argument("--id", type=int, required=False)
    parser.add_argument("--name", type=str, required=False)
    parser.add_argument("--limit", type=int, required=False)
    parser.add_argument("--group_id", type=int, required=False)
    parser.add_argument("--student_id", type=int, required=False)
    parser.add_argument("--subject_id", type=int, required=False)
    parser.add_argument("--teacher_id", type=int, required=False)
    parser.add_argument("--grade", type=int, required=False)
    parser.add_argument("--date", type=str, required=False)

    args = parser.parse_args()
    action = args.action
    Model = MODELS_MAPPER[args.model]

    params = {
        "id": args.id,
        "name": args.name,
        "limit": args.limit,
        "student_id": args.student_id,
        "subject_id": args.subject_id,
        "teacher_id": args.teacher_id,
        "grade": args.grade,
        "date": args.date,
    }

    try:
        if action == ACTIONS["list"]:
            result = list_action(Model, **params)
            for row in result:
                print(f"{row}")
        elif action in [ACTIONS["create"], ACTIONS["update"], ACTIONS["remove"]]:
            execute_action(action, Model, params)
            print(f"{action.capitalize()}d!")
        else:
            print(f'Вибачте! Ми не знаємо що робити з "{action}"')
    except ValueError as error:
        print(error)
    except Exception as error:
        print("[!] Йой! Щось пішло не так!")
        print(error)


if __name__ == "__main__":
    main()
