({
    name: "Led Digit", // Category Name
    description: "Led 7 segments",
    author: "BeeBlock",
    category: "Sensors",
    version: "1.0.0",
    icon: "/static/led7segments.png", // Category icon
    color: "#3d87ff", // Category color (recommend some blocks color)
    blocks: [ // Blocks in Category
        {
            xml: `
                <block type="led_7_segments">
                    <value name="message">
                        <shadow type="text">
                            <field name="TEXT">Hello</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        {
            xml: `
                <block type="led7seg_temperature">
                    <value name="message">
                        <shadow type="text">
                            <field name="TEXT">35</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        "led7seg_clear"
    ]
});