Blockly.defineBlocksWithJsonArray([
    // -> Led 7 Segments
    {
        "type": "led_7_segments",
        "message0": "%3 %2 display %1",
        "args0": [
            {
                "type": "input_value",
                "name": "message",
            },
            {
                "type": "field_grid_dropdown",
                "name": "port",
                "columns": 2,
                "options": [
                    ["PORT1", "PORT1"],
                    ["PORT2", "PORT2"],
                    ["PORT3", "PORT3"],
                    ["PORT4", "PORT4"],
                    ["PORT5", "PORT5"],
                    ["PORT6", "PORT6"],
                ]
            },
            {
                "type": "field_image",
                "src": "/static/MicroBlock/images/icon/led7segments.png",
                "width": 45,
                "height": 45,
                "alt": "led7segments"
            }
        ],
        "inputsInline": true,
        "previousStatement": null,
        "nextStatement": null,
        "colour": "#3d87ff",
        "tooltip": "",
        "helpUrl": ""
    },
    {
        "type": "led7seg_temperature",
        "message0": "%3 %2 display %1 °C",
        "args0": [
            {
                "type": "input_value",
                "name": "message",
            },
            {
                "type": "field_grid_dropdown",
                "name": "port",
                "columns": 2,
                "options": [
                    ["PORT1", "PORT1"],
                    ["PORT2", "PORT2"],
                    ["PORT3", "PORT3"],
                    ["PORT4", "PORT4"],
                    ["PORT5", "PORT5"],
                    ["PORT6", "PORT6"],
                ]
            },
            {
                "type": "field_image",
                "src": "/static/MicroBlock/images/icon/led7segments.png",
                "width": 45,
                "height": 45,
                "alt": "led7segments"
            }
        ],
        "inputsInline": true,
        "previousStatement": null,
        "nextStatement": null,
        "colour": "#3d87ff",
        "tooltip": "",
        "helpUrl": ""
    },
    {
        "type": "led7seg_clear",
        "message0": "%2 %1 clear",
        "args0": [
            {
                "type": "field_grid_dropdown",
                "name": "port",
                "columns": 2,
                "options": [
                    ["PORT1", "PORT1"],
                    ["PORT2", "PORT2"],
                    ["PORT3", "PORT3"],
                    ["PORT4", "PORT4"],
                    ["PORT5", "PORT5"],
                    ["PORT6", "PORT6"],
                ]
            },
            {
                "type": "field_image",
                "src": "/static/MicroBlock/images/icon/led7segments.png",
                "width": 45,
                "height": 45,
                "alt": "led7segments"
            }
        ],
        "inputsInline": true,
        "previousStatement": null,
        "nextStatement": null,
        "colour": "#3d87ff",
        "tooltip": "",
        "helpUrl": ""
    },
]);