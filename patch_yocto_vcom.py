import xml.etree.ElementTree as ET

file_path = '/home/genius/acrn-work/my_scenario_rt.xml'
tree = ET.parse(file_path)
root = tree.getroot()

for vm in root.findall('vm'):
    name = vm.find('name')
    if name is not None and name.text == 'PRE_RT_VM1':
        # 1. PRE_LAUNCHED_VM に変更
        vm.find('load_order').text = 'PRE_LAUNCHED_VM'
        
        # 2. VUART (仮想シリアルポート) の停止
        vuart = vm.find('console_vuart')
        if vuart is not None:
            vuart.text = 'None'
        else:
            ET.SubElement(vm, 'console_vuart').text = 'None'
            
        # 3. メモリの割り当て (1024MB)
        mem = vm.find('memory')
        if mem is None:
            mem = ET.SubElement(vm, 'memory')
            size = ET.SubElement(mem, 'size')
            size.text = '1024'
        else:
            size_elem = mem.find('size')
            if size_elem is not None:
                size_elem.text = '1024'
            else:
                size_elem = ET.SubElement(mem, 'size')
                size_elem.text = '1024'
                
        # 4. os_config ブロックの作り直し（カーネルタグ整合性）
        os_cfg = vm.find('os_config')
        if os_cfg is not None:
            vm.remove(os_cfg)
            
        os_cfg = ET.SubElement(vm, 'os_config')
        ET.SubElement(os_cfg, 'name').text = 'Yocto'
        ET.SubElement(os_cfg, 'kern_type').text = 'KERNEL_BZIMAGE'
        ET.SubElement(os_cfg, 'kern_mod').text = 'Linux_bzImage_rt'
        ET.SubElement(os_cfg, 'ramdisk_mod').text = 'Linux_initrd_rt'
        # シリアルコンソールが無いので bootargs から console=... を削除
        ET.SubElement(os_cfg, 'bootargs').text = 'root=/dev/ram0 rw init=/bin/sh loglevel=7 ignore_loglevel'

ET.indent(tree, space="  ")
tree.write(file_path, encoding='utf-8', xml_declaration=False)
