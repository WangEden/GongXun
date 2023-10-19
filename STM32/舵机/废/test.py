import xlwt

# 创建工作簿
wb = xlwt.Workbook()
# 创建表单
sh = wb.add_sheet('test')
# 创建字体对象
font = xlwt.Font()
# 字体加粗
font.bold = True
alm = xlwt.Alignment()
# 设置左对齐
alm.horz = 0x01
# 创建样式对象
style1 = xlwt.XFStyle()
style2 = xlwt.XFStyle()
style1.font = font
style2.alignment = alm
# write 方法参数1：行，参数2：列，参数3：内容
sh.write(0, 1, '姓名', style1)
sh.write(0, 2, '年龄', style1)
sh.write(1, 1, '张三')
sh.write(1, 2, 50, style2)
sh.write(2, 1, '李四')
sh.write(2, 2, 30, style2)
sh.write(3, 1, '王五')
sh.write(3, 2, 40, style2)
sh.write(4, 1, '赵六')
sh.write(4, 2, 60, style2)
sh.write(5, 0, '平均年龄', style1)
