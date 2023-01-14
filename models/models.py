# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
from io import StringIO
import pandas as pd
import os
import textwrap
from pathlib import Path
import xml.etree.ElementTree as ET


dir = Path(__file__).resolve().parent


class odoo_refine(models.Model):
    _name = 'odoo_refine.odoo_refine'
    _description = 'Refine messy Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    file = fields.Binary("Upload file", requered=True)

    def read_file(self):
        string = str(base64.b64decode(self.file), 'utf-8')
        data = StringIO(string)
        df = pd.read_csv(data)
        valid_name = str(self.name).replace(" ", "")
        file_path = f"{dir}\{valid_name}.py"
        description = f"Refine {valid_name}"
        model_string, tree_string, form_string = refine_fields(df.columns)
        with open(file_path, 'w') as f:
            model = write_model(valid_name, description, model_string)
            f.write(textwrap.dedent(model))
        import_model(valid_name)
        xml_file_path = f"{dir.parent}/views/refine_dashboard.xml"
        print(xml_file_path)
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        menu = ET.SubElement(root, "field")
        print(tree)
        print(root)
        print(ET.tostring(root))
        with open(xml_file_path, "wb") as f:
            f.write(ET.tostring(root))
        # lines = lines[:-1]
            # xml_code = write_xml(valid_name, tree_string, form_string)
            # file.writelines(lines)
            # file.write(xml_code)
        print('Execution completed.')

        # for i in range(sheet.nrows):
        #     if i == 0:
        #         continue
        #     if i == 1:
        #         name = sheet.cell(i, 0).value
        #         vat = sheet.cell(i, 5).value


        # for rec in self:
        #     print("self.file", rec.file.text)

def refine_fields(columns):
    model_string = ''
    tree_string = ''
    form_string = ''
    for col in columns:
        name_valid = str(col).replace(" ", "").replace('/', '_')
        model_string += f'    {name_valid} = fields.Char(string="{name_valid.capitalize()}", required=True, tracking=True)\n'
        tree_string += f'            <field name="{name_valid}"/>'
        form_string += f'                <field name="{name_valid}"/>'

    return model_string, tree_string, form_string

def write_model(name, description, fields):

    string = f'''\
from odoo import models, fields, api



class {name.capitalize()}(models.Model):
    _name = "{name}"
    _description = "Refine {description} data"
'''
    string += fields
    print(string)
    return string

def import_model(model_name):
    with open(f"{dir}\__init__.py", 'a') as f:
        f.write(f", {model_name}")

def write_xml(file_name, tree_string, form_string):
    string = f'''\
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
    <field name="res_model">file_name</field>
    <field name="view_mode">tree,form</field>
</record>


<menuitem
        id="menu_{file_name}_master"
        name="{file_name.capitalize()}"
        parent="menu_projects_master"
        action="action_{file_name}_refine"
        sequence="10"/>
'''
    return string