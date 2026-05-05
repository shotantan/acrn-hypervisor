import xml.etree.ElementTree as ET

tree = ET.parse('/home/genius/acrn-work/my_scenario_rt.xml')
root = tree.getroot()

for vm in root.findall('vm'):
    if vm.find('name') is not None and vm.find('name').text == 'PRE_RT_VM1':
        vm.find('load_order').text = 'PRE_LAUNCHED_VM'
        
        # Remove or set console_vuart to None
        vuart = vm.find('console_vuart')
        if vuart is None:
            vuart = ET.SubElement(vm, 'console_vuart')
        vuart.text = 'None'
        
        # Add memory
        mem = vm.find('memory')
        if mem is None:
            mem = ET.SubElement(vm, 'memory')
            size = ET.SubElement(mem, 'size')
            size.text = '1024'
        else:
            mem.find('size').text = '1024'
            
        # Add os_config
        os_cfg = vm.find('os_config')
        if os_cfg is None:
            os_cfg = ET.SubElement(vm, 'os_config')
            ET.SubElement(os_cfg, 'name').text = 'Yocto'
            ET.SubElement(os_cfg, 'kern_type').text = 'KERNEL_BZIMAGE'
            ET.SubElement(os_cfg, 'kern_mod').text = 'Linux_bzImage_rt'
            ET.SubElement(os_cfg, 'ramdisk_mod').text = 'Linux_initrd_rt'
            ET.SubElement(os_cfg, 'bootargs').text = 'console=hvc0 root=/dev/ram0 rw init=/bin/sh loglevel=7 ignore_loglevel'
        else:
            os_cfg.find('kern_mod').text = 'Linux_bzImage_rt'
            os_cfg.find('ramdisk_mod').text = 'Linux_initrd_rt'
            # Using hvc0 or just removing ttyS parameter so it doesn't conflict
            os_cfg.find('bootargs').text = 'console=hvc0 root=/dev/ram0 rw init=/bin/sh loglevel=7 ignore_loglevel'

ET.indent(tree, space="  ")
tree.write('/home/genius/acrn-work/my_scenario_rt.xml', encoding='utf-8', xml_declaration=False)
