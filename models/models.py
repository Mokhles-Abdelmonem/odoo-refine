# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import base64
from io import StringIO
import pandas as pd
import os
import textwrap
from pathlib import Path
import xml.etree.ElementTree as ET
import time
import threading


dir = Path(__file__).resolve().parent


class odoo_refine(models.Model):
    _name = 'odoo_refine.odoo_refine'
    _description = 'Refine messy Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    file = fields.Binary("Upload file", requered=True)
    state = fields.Selection([
        ('has_project', 'Has project'),
        ('no_project', 'No project'),
        ('done', 'Done')],
        default='no_project')

    def start_project(self):
        self.state = 'has_project'
        string = str(base64.b64decode(self.file), 'utf-8')
        data = StringIO(string)
        df = pd.read_csv(data)
        valid_name = str(self.name).replace(" ", "")
        description = f"Refine {valid_name}"
        model_string, tree_string, form_string, refined_columns = refine_fields(df.columns)
        write_model(valid_name, description, model_string)
        import_model(valid_name)
        write_xml(valid_name, tree_string, form_string)
        write_task = threading.Thread(target=write_access,args=(valid_name,))
        write_task.start()
        # write_access(valid_name)

    def start_refining(self):
        string = str(base64.b64decode(self.file), 'utf-8')
        data = StringIO(string)
        df = pd.read_csv(data)
        valid_name = str(self.name).replace(" ", "")
        refined_columns = []
        for col in df.columns:
            name_valid = str(col).replace(" ", "").replace('/', '_')
            refined_columns.append(name_valid)

        the_model = self.env[f'{valid_name}']
        self.state = 'done'
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }
        # write_task = threading.Thread(target=create_record,args=(the_model, df, refined_columns,))
        # write_task.start()


        create_record(the_model, df, refined_columns)
        print("________________________create_record success_____________________________")

def refine_fields(columns):
    model_string = ''
    tree_string = ''
    form_string = ''
    refined_columns = []
    for col in columns:
        name_valid = str(col).replace(" ", "").replace('/', '_')
        model_string += f'    {name_valid} = fields.Char(string="{name_valid.capitalize()}", required=True, tracking=True)\n'
        tree_string += f'            <field name="{name_valid}"/>'
        form_string += f'                <field name="{name_valid}"/>'
        refined_columns.append(name_valid)
    return model_string, tree_string, form_string, refined_columns

def write_model(name, description, fields):

    string = f'''\
from odoo import models, fields, api



class {name.capitalize()}(models.Model):
    _name = "{name}"
    _description = "Refine {description} data"
'''

    string += fields
    file_path = f"{dir}\{name}.py"
    with open(file_path, 'w') as f:
        f.write(textwrap.dedent(string))



def import_model(model_name):
    with open(f"{dir}\__init__.py", 'a') as f:
        f.write(f", {model_name}")

def write_xml(file_name, tree_string, form_string):
    string = f'''\
<root>
<record id="view_{file_name}_tree" model="ir.ui.view">
    <field name="name">{file_name}.view.tree</field>
    <field name="model">{file_name}</field>
    <field name="arch" type="xml">
        <tree>
{tree_string}
        </tree>
    </field>
</record>
<record id="view_{file_name}_form" model="ir.ui.view">
    <field name="name">{file_name}.view.tree</field>
    <field name="model">{file_name}</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
{form_string}
            </sheet>
        </form>
    </field>
</record>

<record id="action_{file_name}_refine" model="ir.actions.act_window">
    <field name="name">{file_name.capitalize()}</field>
    <field name="type">ir.actions.act_window</field>
    <field name="res_model">{file_name}</field>
    <field name="view_mode">tree,form</field>
</record>


<menuitem
        id="menu_{file_name}_master"
        name="{file_name.capitalize()}"
        parent="menu_projects_master"
        action="action_{file_name}_refine"
        sequence="10"/>
</root>
'''

    xml_file_path = f"{dir.parent}/views/refine_dashboard.xml"
    src_tree = ET.parse(xml_file_path)
    root = src_tree.getroot()
    xml_tree = ET.fromstring(string)
    for element in xml_tree:
        root.append(element)

    et = ET.ElementTree(root)
    et.write(xml_file_path, encoding='utf-8', xml_declaration=True)


def create_record(the_model, df, refined_columns):
    df.columns =refined_columns
    df = df.to_dict('records')
    rows = df
    for index in range(len(rows)):
        print(rows[index])
        the_model.create(rows[index])


def write_access(model_name):
    print("________________________from access page _____________________________")
    time.sleep(5)
    access_file_path = f"{dir.parent}/security/ir.model.access.csv"
    string = f"\nodoo_refine.access_{model_name},access_{model_name},odoo_refine.model_{model_name},base.group_user,1,1,1,1"
    with open(access_file_path, 'a') as f:
        f.write(string)
    print("________________________after access page _____________________________")

