function check_if_top_block_has_hat(block){
   if (block.getRootBlock().hat === 'cap') return true;
   else return false;
}

Blockly.Python['led_7_segments'] = function(block) {
   if (!check_if_top_block_has_hat(block)) return '';

   Blockly.Python.definitions_['from_BeeBrain_import_bee'] = 'from BeeBrain import bee';

   Blockly.Python.definitions_['from_BeeLedSegment_import_BeeLedSegment'] = 'from BeeLedSegment import BeeLedSegment';

   var port = block.getFieldValue('port');
   Blockly.Python.definitions_['led7seg_BeeLedSegment'] = `leg7seg = BeeLedSegment(bee.${port})`;
   var message = Blockly.Python.valueToCode(block, 'message', Blockly.Python.ORDER_ATOMIC);
   var code = `leg7seg.display(${message})\n`;

   return code;
};

Blockly.Python['led7seg_temperature'] = function(block) {
   if (!check_if_top_block_has_hat(block)) return '';

   Blockly.Python.definitions_['from_BeeBrain_import_bee'] = 'from BeeBrain import bee';

   Blockly.Python.definitions_['from_BeeLedSegment_import_BeeLedSegment'] = 'from BeeLedSegment import BeeLedSegment';

   var port = block.getFieldValue('port');
   Blockly.Python.definitions_['led7seg_BeeLedSegment'] = `leg7seg = BeeLedSegment(bee.${port})`;
   var message = Blockly.Python.valueToCode(block, 'message', Blockly.Python.ORDER_ATOMIC);
   var code = `leg7seg.temperature(${message})\n`;

   return code;
};

Blockly.Python['led7seg_temperature'] = function(block) {
   if (!check_if_top_block_has_hat(block)) return '';

   Blockly.Python.definitions_['from_BeeBrain_import_bee'] = 'from BeeBrain import bee';

   Blockly.Python.definitions_['from_BeeLedSegment_import_BeeLedSegment'] = 'from BeeLedSegment import BeeLedSegment';

   var port = block.getFieldValue('port');
   Blockly.Python.definitions_['led7seg_BeeLedSegment'] = `leg7seg = BeeLedSegment(bee.${port})`;
   var code = `leg7seg.clear()\n`;

   return code;
};