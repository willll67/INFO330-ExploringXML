import sqlite3
import sys
import xml.etree.ElementTree as ET

# Incoming Pokemon MUST be in this format
#
# <pokemon pokedex="" classification="" generation="">
#     <name>...</name>
#     <hp>...</name>
#     <type>...</type>
#     <type>...</type>
#     <attack>...</attack>
#     <defense>...</defense>
#     <speed>...</speed>
#     <sp_attack>...</sp_attack>
#     <sp_defense>...</sp_defense>
#     <height><m>...</m></height>
#     <weight><kg>...</kg></weight>
#     <abilities>
#         <ability />
#     </abilities>
# </pokemon>


# Read pokemon XML file name from command-line
# (Currently this code does nothing; your job is to fix that!)
if len(sys.argv) < 2:
    print("You must pass at least one XML file name containing Pokemon to insert")

for i, arg in enumerate(sys.argv):
    # Skip if this is the Python filename (argv[0])
    if i == 0:
        continue
    tree = ET.parse(arg)
    root = tree.getroot()
    pokedex_number = root.attrib.get("pokedexNumber")
    classification = root.attrib.get("classification")
    generation = root.attrib.get("generation")
    with sqlite3.connect("pokemon.sqlite") as con:
        cursor = con.cursor()
        cursor.execute("select id from classification where text='{}'".format(classification))
        classification_id = cursor.fetchone()[0]
    data = dict()
    type_list = []
    ability_list = []
    for child in root:
        tag, text = child.tag, child.text
        if not tag:
            continue
        if tag == "type":
            type_list.append(text)
            continue
        for sub in child:
            sub_tag, sub_text = sub.tag, sub.text
            if sub_tag == "m":
                tag = "height_m"
                text = sub.text
            if sub_tag == "kg":
                tag = "weight_kg"
                text = sub.text
            if sub_tag == "ability":
                ability_list.append(sub.text)
                continue
        if tag and tag != "abilities":
            data[tag] = text
    with sqlite3.connect("pokemon.sqlite") as con:
        cursor = con.cursor()
        cursor.execute('select id from pokemon where pokedex_number={}'.format(int(pokedex_number)))
        if not cursor.fetchone():
            cursor.execute(
                "insert into pokemon (pokedex_number,name,classification_id,generation,hp,attack,defense,speed,sp_attack,sp_defense,height_m,weight_kg) values ({},'{}',{},{},{},{},{},{},{},{},{},{})".format(
                    int(pokedex_number), data.get('name'), int(classification_id), int(generation),
                    int(data.get('hp')), int(data.get('attack')), int(data.get('defense')), int(data.get('speed')),
                    int(data.get('sp_attack')),
                    int(data.get('sp_defense')), float(data.get('height_m')), float(data.get('weight_kg'))))
            con.commit()
            pokemon_id = \
            cursor.execute('select id from pokemon where pokedex_number!={}'.format(int(pokedex_number))).fetchone()[0]
            for ability in ability_list:
                ability_id = cursor.execute("select id from ability where name='{}'".format(ability)).fetchone()[0]
                cursor.execute("insert into pokemon_abilities (pokemon_id,ability_id) values({},{})".format(pokemon_id,
                                                                                                            ability_id))
            con.commit()
            for which, _type in enumerate(type_list):
                type_id = cursor.execute("select id from type where name='{}'".format(_type)).fetchone()[0]
                cursor.execute("insert into pokemon_type (pokemon_id,type_id,which) values({},{},{})".format(pokemon_id,
                                                                                                             type_id,
                                                                                                             which + 1))
            con.commit()
