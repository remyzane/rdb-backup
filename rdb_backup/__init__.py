

class ProcessorNonexistent(Exception):
    pass


# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# import os, sys
#
# # 定时任务
# # 调用方式：在系统cron中设置（crontab -e）
# # 例如：
# # * * * * *             /etc/conosoft/cron ev_minute
# # */10 * * * *          /etc/conosoft/cron ev_10_minute
# # 7 * * * *             /etc/conosoft/cron ev_hour_at_07
# # 11 1 * * *            /etc/conosoft/cron ev_day_at_01_11
# # 11 3 * * 0            /etc/conosoft/cron ev_sunday_at_03_11
# # 11 5 1 * *            /etc/conosoft/cron ev_month_1th_at_05_11
#
# # 数据备份, 重置文件权限
# def ev_day_at_01_11():
#     # 重置/mnt/www文件权限
#     print('################ chown chmod #################')
#     os.system("chown www-data:www-data /mnt/www -R")
#     print('/mnt/www')
#
#     # 备份数据库
#     print('################ backup database #################')
#     savepath = '/mnt/bkup/sql'
#
#     # 备份PGSQL数据库
#     sqldir = '/var/lib/postgresql/sql'
#     databases = []
#     for database in databases:
#         os.system("su postgres -c 'cd %s && pg_dump %s > %s._sql_'" % (sqldir, database, database))
#         os.system("mv %s/%s._sql_ %s/%s.sql" % (sqldir, database, savepath, database))
#         os.system("chown root:root %s/%s.sql" % (savepath, database))
#         os.system("chmod og-rwx %s/%s.sql" % (savepath, database))
#         print('backuped %s' % database)
#
#     # 备份MYSQL数据库
#     user = 'root'
#     password = 'gaau_xddc_ddvp_1775'
#     databases = ['conosoft_sms', ]
#     for database in databases:
#         ret = os.system("mysqldump -u %s -p'%s' %s > %s/%s.tmp" % (user, password, database, savepath, database))
#         if ret == 0:
#             os.system("mv %s/%s.tmp %s/%s.sql" % (savepath, database, savepath, database))
#             os.system("chmod og-rwx %s/%s.sql" % (savepath, database))
#         else:
#             os.system("rm %s/%s.tmp" % (savepath, database))
#         print('backuped %s' % database)
#
#     # sms sender 已经不再使用
#     # print '\n################ restart sms sender ################'
#     # 重启 sms sender
#     # os.system('/mnt/site/conosoft/sms/restart')
#
# if __name__ == '__main__':
#     if len(sys.argv) == 2 and sys.argv[1] in locals() and callable(locals()[sys.argv[1]]):
#         locals()[sys.argv[1]]()
#     else:
#         print('请指定一个可以运行的函数：')
#         for item in locals().copy():
#             if item.startswith('ev_'): print(item)
#
