import xml.etree.ElementTree as ET

tree = ET.parse('/home/genius/acrn-work/my_scenario_rt.xml')
root = tree.getroot()

for vm in root.findall('vm'):
    if vm.find('name') is not None and vm.find('name').text == 'PRE_RT_VM1':
        # Change console_vuart
        vuart = vm.find('console_vuart')
        if vuart is not None:
            vuart.text = 'COM Port 3'
        
        # Change bootargs
        os_cfg = vm.find('os_config')
        if os_cfg is not None:
            bootargs = os_cfg.find('bootargs')
            if bootargs is not None:
                # Replace ttyS1 with ttyS2 (ttyS0=COM1, ttyS1=COM2, ttyS2=COM3)
                bootargs.text = bootargs.text.replace('ttyS1', 'ttyS2')

ET.indent(tree, space="  ")
tree.write('/home/genius/acrn-work/my_scenario_rt.xml', encoding='utf-8', xml_declaration=False)
