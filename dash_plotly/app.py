from dash import Dash, dcc, html, dash_table, Input, Output, ctx, callback
import dash_bootstrap_components as dbc

import json
import os
from collections import OrderedDict
from datetime import date


from rdkit import Chem
from rdkit.Chem.Draw import IPythonConsole
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import Draw
IPythonConsole.ipython_useSVG=True
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
from PIL import Image


from CGRtools.files import MRVWrite, MRVRead
# from CIMtools.preprocessing import RDTool
from dash_marvinjs import DashMarvinJS
from io import BytesIO, StringIO


app = Dash(__name__, title='Storage', update_title=None, external_stylesheets=[dbc.themes.BOOTSTRAP])

table_1 = html.Div([[html.Button(str(i), id=f'1-btn-{i}', className="btn") for i in range(1, 96)],
                        html.Div(id='container-button-1'), ])


table_2 = html.Div([[html.Button(str(i), id=f'2-btn-{i}', className="btn") for i in range(1, 12)],
                        html.Div(id='container-button-2'), ])



tab_content = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([

                    dbc.Card(  # рамка для кнопок
                    dbc.CardBody([  # отступы для кнопок от рамки

                        html.Div(html.H3("Выберите номер хранилища:")),
                        dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
                            dcc.Tab(label='Хранилище №1', children=[table_1]),
                            dcc.Tab(label='Хранилище №2', children=[table_2]),
                        ]),
                        html.Div(id='tabs-example-content-1')

                ]), ),  # card, cardbody
                ], width=3),
                dbc.Col([
                    "Информация про соединение",
                            html.Div(
                                dbc.Card(  # рамка для кнопок
                                dbc.CardBody([  # отступы для кнопок от рамки
                                    dbc.Row([
                                        dbc.Col([ html.Div([dbc.Card(dbc.CardBody(["Соединение №: ", dcc.Input(id="input_number", disabled=True)])) ]),
                                                 html.Div([dbc.Card(dbc.CardBody(["Smiles: ", dbc.Input(id="input_smiles", type="text", disabled=True)])) ])
                                                 ], width=5),

                                        dbc.Col([html.Div([dbc.Card(dbc.CardBody(["Рисунок: ", html.Div(id='formula')]))
                                                           ]), ], ),

                                        ]),
                                ]),),  # card, cardbody

                            ),

                    html.Div(
                        dbc.Card(  # рамка
                            dbc.CardBody([  # отступы

                                dbc.Row([
                                    dbc.Col([html.Div([dbc.Card(dbc.CardBody(["Date: ", dcc.DatePickerSingle(
                                                                                        id='input_date',
                                                                                        min_date_allowed=date(2020, 8, 5),
                                                                                        initial_visible_month=date(2024, 8, 5),
                                                                                        disabled=True,
                                                                                    ),  ])) ]),
                                            html.Div([dbc.Card(dbc.CardBody(["Volume: ", dcc.Input(id='input_volume', type='number', debounce=True, value="", step=0.0001, min=0.0, max=5, disabled=True)])) ]),
                                            html.Div([dbc.Card(dbc.CardBody(["Mols: ", dcc.Input(id='input_mols', type='number', debounce=True, value="", step=1, min=0, max=10, disabled=True)])) ]),
                                            html.Div([dbc.Card(dbc.CardBody(["State: ", dbc.Select(["liquid", "gas"], value="", id="input_state", disabled=True),])) ]),
                                            html.Div([dbc.Card(dbc.CardBody(["Density: ", dcc.Input(id='input_density', type='number', debounce=True, value="", step=0.0001, min=0.0, max=10, disabled=True)])) ]),
                                            html.Div([dbc.Card(dbc.CardBody(["Concentration: ", dcc.Input(id='input_concentration', type='number', debounce=True, value="", step=0.0001, min=0.0, max=10, disabled=True)], )) ]),
                                            html.Div([dbc.Card(dbc.CardBody(["Solvent: ", dcc.Textarea(id='input_solvent', value="", style={'width': '100%'}, disabled=True,)])) ]),
                                            dbc.Button("Edit", id="btn-edit"),
                                            dbc.Button("Save Changes", id="btn-save_changes", disabled=True),
                                            dcc.Download(id="save_changes"),
                                            dbc.Button("Download", id="btn-download", disabled=True),
                                            dcc.Download(id="download")
                                             ], width=3
                                        ),

                                    dbc.Col([html.Div([dbc.Card(dbc.CardBody([DashMarvinJS(id='editor',
                                                                                               marvin_url=app.get_asset_url(
                                                                                                   'marvin/editor.html'),
                                                                                               marvin_width='100%',
                                                                                               marvin_height="700px",
                                                                                               marvin_button={
                                                                                                   'name': 'Upload and Predict',
                                                                                                   'image-url':
                                                                                                       'data:image/png;base64,'
                                                                                                       'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9btSKVDnYQcchQxcGCaBFHrUIRKoRaoVUHk0u/oElDkuLiKLgWHPxYrDq4OOvq4CoIgh8gjk5Oii5S4v+SQosYD4778e7e4+4d4G9UmGp2TQCqZhnpZELI5laF4Ct6EEAYcYxJzNTnRDEFz/F1Dx9f72I8y/vcn6NfyZsM8AnEs0w3LOIN4ulNS+e8TxxhJUkhPiceN+iCxI9cl11+41x02M8zI0YmPU8cIRaKHSx3MCsZKnGcOKqoGuX7sy4rnLc4q5Uaa92TvzCU11aWuU5zGEksYgkiBMiooYwKLMRo1Ugxkab9hId/yPGL5JLJVQYjxwKqUCE5fvA/+N2tWZiadJNCCaD7xbY/RoDgLtCs2/b3sW03T4DAM3Cltf3VBjDzSXq9rUWPgPA2cHHd1uQ94HIHGHzSJUNypABNf6EAvJ/RN+WAgVugb83trbWP0wcgQ12lboCDQ2C0SNnrHu/u7ezt3zOt/n4AkLdys63OCbEAAAAGYktHRAD/AP8A/6C9p5MAAAAJcEhZcwAACcUAAAnFAYeExPQAAAAHdElNRQfmBgMQACi4rwP7AAACFUlEQVR42u3dTU7DMBSF0TyrE5bICllihzBCQkhIxM2P7Xu+GROa9J2YpE3ptim6St3xt4+3z58/P9+fBUDg4H+XBqEMPxtBGX42gjL8bARl+NkIyvCzEZThZyMow89GUIafjaAMPxtBGX42gjL8bARl+NkIyvCzEZThZyMow89GUIafjaAMPxtBGX42gjL8bAQtYfg9gzhieDPAbYafjWD4FeDuJXj1O4Laqkf/kYN79XeNvAo0R372StAMPxtBM/xsBG2VYV45mJUQNEf++Y85Mpg2+2DvfHJH377/NPV7AXue3LM/G/jq9gEw2OsKKR8ObZuiAwAAASAABIACe1x9edXbbJdlszwvNfoOHrXDV70OcOd7/z3b3Hp28M6dHPnmiru3refxnQMs1l4Ebcajb8RVYNZb160A4atAW124rAACYPzrcQACnmwAFh/+jDCb4R+/jTNBeDga5tj/s67CnAQ6BxAAAkAACAABIAAEgAAQAAJAAAgAASAABIAAEAACQAAIAAEgAASAABAAAkAACAABIAAEgAAQAAJAANya/y1oBYAlHcAK3/ULwAEI/hpy4p+JxxaacwLnAAJAAAAgAASAABAAAkAACAABIAAEgAAQAAJAAAgAASAABIDW6LTbws/6vntZAQSAABAAAkBXAfBhSiuAJmnPwQpAeLuXdS/wrHP0dwGAYJ3hdwMAYf7Bf/cFhGgHu/GCd/wAAAAASUVORK5CYII=',
                                                                                                   'toolbar': 'N'
                                                                                                   })]))
                                                       ]), ], ),


                                ]),
                            ]), ),  # card, cardbody
                    )

                ], width=9),
                ], align='center'),
            ])
    )
])


@app.callback([Output('editor', 'upload'),
           Output('smiles2', 'value'),],
          [Input('editor', 'download')],
          prevent_initial_call=True)
def standardize_reaction(value):
    if value:
        with BytesIO(value.encode()) as f, MRVRead(f) as i:
            s = next(i)
            s.canonicalize()
        with StringIO() as f:
            with MRVWrite(f) as o:
                o.write(s)
            value = f.getvalue()
    return value, str(s)


@app.callback(
    Output("download", "children"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return 'tubes_storage_1.json'


@app.callback(
    [Output("save_changes", "children"),],
    [Input("btn-save_changes", "n_clicks"),
     Input("input_volume", "value"),
     Input("input_mols", "value"),
     Input("input_state", "value"),
     Input("input_density", "value"),
     Input("input_concentration", "value"),
     Input("input_solvent", "value")],
    prevent_initial_call=True,
)
def change_data(n_clicks, val_volume, val_mols, val_state, val_density, val_concentration, val_solvent):

    if n_clicks > 0:
        with open('tubes_storage_1.json', 'r') as r:
            r = json.load(r)
            r['1']['volume'] = val_volume
            r['1']['mols'] = val_mols
            r['1']['state'] = val_state
            r['1']['density'] = val_density
            r['1']['concentration'] = val_concentration
            r['1']['solvent']["smiles"] = val_solvent
        with open('tubes_storage_1.json', 'w') as w:
            w = json.dump(r, w)
    return None


@app.callback(
     [Output('btn-save_changes', "disabled"),
      Output('input_volume', "disabled"),
      Output('input_mols', "disabled"),
      Output('input_state', "disabled"),
      Output('input_density', "disabled"),
      Output('input_concentration', "disabled"),
      Output('input_solvent', "disabled"),
      Output("btn-download", "disabled"),
      Output('input_smiles', 'disabled'),
      ],
      [Input('btn-edit', 'n_clicks')],
      prevent_initial_call=True
)
def enable(n_clicks):
    if n_clicks % 2 != 0:
        return [False] * 9
    else:
        return [True] * 9



@app.callback(
    [Output('input_number', 'value'),
    Output('input_smiles', 'value'),
    Output('formula', 'children'),
    Output('input_volume', 'value'),
    Output('input_mols', 'children'),
    Output('input_state', 'value'),
    Output('input_density', 'value'),
    Output('input_concentration', 'value'),
    Output('input_solvent', 'value')],

    [Input(f'1-btn-{i}', 'n_clicks') for i in range(1, 96)],
    prevent_initial_call=True
)
def get_chemical_data(btn_number):
    with open('tubes_storage_1.json') as file:
        file = json.load(file)
        if btn_number not in file.keys():
            return (f"Сoединение №: {btn_number}",
                    f"Smiles: ",
                    None,
                    f"Volume: ",
                    f"Mols: ",
                    f"State: ",
                    f"Density: ",
                    f"Concentration: ",
                    f"Solvent: ")

        values = file[btn_number]
        try:
            smiles = values["smiles"]
            volume = values["volume"]
            mols = values["mols"]
            state = values["state"]
            density = values["density"]
            concentration = values["concentration"]
            solvent = values["solvent"]["smiles"]
            image_path = f"./assets/images/formula{btn_number}.png"
            if not os.path.isfile(image_path):
                formula = Chem.MolFromSmiles(smiles)
                d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                d.DrawMolecule(formula)
                d.FinishDrawing()
                png = d.GetDrawingText()
                open(image_path, 'wb+').write(png)

            return (f"Сoединение №: {btn_number}",
                    smiles,
                    html.Img(src=image_path),
                    volume,
                    mols,
                    state,
                    density,
                    concentration,
                    solvent)
        except:
            return (f"Сoединение №: {btn_number}",
                    f"Smiles: ",
                    None,
                    f"Volume: ",
                    f"Mols: ",
                    f"State: ",
                    f"Density: ",
                    f"Concentration: ",
                    f"Solvent: ")

def displayClick(*btns):
    for i in range(1, len(btns) + 1):
        if f"1-btn-{i}" == ctx.triggered_id:
            return get_chemical_data(str(i))
    return None


tabs = dbc.Tabs(
    [
        dbc.Tab(tab_content, label="Хранилище")
    ]
)

app.layout =tabs
if __name__ == '__main__':
    app.run_server(debug=True)
