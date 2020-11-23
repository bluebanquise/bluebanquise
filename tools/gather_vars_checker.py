#!/usr/bin/env python3

import glob
import logging
import os
import sys
import yaml


def usage(command):
    print(f"Usage: {command} main.yml")


# Get tags of the include_vars task that gather OS variables
def get_gather_vars_tags(task):
    gather_task_tags = list()
    for k, v in task.items():
        if k == 'name' and v == 'include_vars ░ Gather OS specific variables':
            if 'tags' in task:
                gather_task_tags = task['tags']

    return gather_task_tags


# Return the list of variables defined in a role
def get_role_variables(rolepath):
    variables = list()
    for varsfile in glob.glob(os.path.join(rolepath, 'vars/*.yml')):
        logging.info(f'Load variables from: {varsfile}')
        with open(varsfile, 'r') as fd:
            for k in yaml.load(fd, Loader=yaml.SafeLoader):
                variables.append(k)

    if len(variables):
        logging.info(f'List of variables: {sorted(set(variables))}')

    return sorted(set(variables))


# Search a list of variables in a dictionary
def lookup_vars(task, variables):
    for var in variables:
        for k, v in task.items():
            if hasattr(v, '__iter__') and var in v:
                logging.debug(f'lookup_vars: Found {var} in {v}')
                return True
            elif isinstance(v, dict) and lookup_vars(v, [var]):
                return True

    return False


# Return a dict with matching task index as key
def search_variables_in_templates(rolepath, variables):
    result = list()
    for templatefile in glob.glob(os.path.join(rolepath, 'templates/*.j2')):
        logging.info(f'Searching {variables} in: {templatefile}')
        with open(templatefile, 'r') as fd:
            for line in fd:
                if any(var in line for var in variables):
                    result.append(os.path.relpath(templatefile,
                                  os.path.join(rolepath, 'templates')))

    return result


# Return the list of tags
def search_variables_in_tasks(rolepath, variables, templates):
    result = list()
    for tasksfile in glob.glob(os.path.join(rolepath, 'tasks/*.yml')):
        logging.info(f'Searching {variables} in: {tasksfile}')
        with open(tasksfile, 'r') as fd:
            for task in yaml.load(fd, Loader=yaml.SafeLoader):
                # Search for any variable in task and append list of tags
                if lookup_vars(task, variables) and 'tags' in task:
                    result.extend(task['tags'])

                # A variable might be use in a template, append its tags
                if 'template' in task and 'tags' in task:
                    if any(tpl in task['template']['src']
                           for tpl in templates):
                        logging.debug(f'DBG: {task}')
                        result.extend(task['tags'])

        logging.debug(f'Found tags {result} in {tasksfile}')

    return result


def main():

    # TODO
    # https://docs.github.com/en/free-pro-team@latest/actions/reference/workflow-commands-for-github-actions#setting-an-error-message
    logging.basicConfig(format="")

    if len(sys.argv) != 2:
        usage(sys.argv[0])
        exit(1)

    rc = 0

    # Loop over the path (can be a glob)
    for rolepath in glob.glob(sys.argv[1]):

        # 1) list vars in the role (vars/*.yml)
        rolevars = get_role_variables(rolepath)

        # 2) search for these vars in templates and tasks
        # If there is a match in a template, search the task
        if len(rolevars):
            tpl_vars = search_variables_in_templates(rolepath, rolevars)
            tsk_vars = search_variables_in_tasks(rolepath, rolevars, tpl_vars)

        # 3) if found, ensure the tags of the tasks are in gathers vars
            for task in glob.glob(os.path.join(rolepath, 'tasks/main.yml')):
                with open(task, 'r') as fd:
                    logging.info(f'Open file: {task}')
                    play = yaml.load(fd, Loader=yaml.SafeLoader)
                    gather_vars_tags = get_gather_vars_tags(play[0])
                    tasks_tags = tsk_vars

                    logging.info(f'List of tags in the gather vars task:\n'
                                 f'{yaml.dump(gather_vars_tags)}\n'
                                 f'List of tags in the other tasks:\n'
                                 f'{yaml.dump(tasks_tags)}')

                    missing_tags = [e for e in tasks_tags
                                    if e not in gather_vars_tags]
                    if len(missing_tags) > 0:
                        logging.error(f'{task}\nList of missing tags:\n'
                                      f'{yaml.dump(missing_tags)}')
                        rc = 1

    sys.exit(rc)


if __name__ == "__main__":
    main()
