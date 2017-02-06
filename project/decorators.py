from waffle.decorators import waffle_flag


edit_project_detail = [waffle_flag('edit_project_detail', 'project:list')]
create_sprint = [waffle_flag('create_sprint', 'project:list')]
create_project = [waffle_flag('create_project', 'project:list')]
delete_project = [waffle_flag('delete_project', 'project:list')]
