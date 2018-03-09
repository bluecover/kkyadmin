#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


PRIVILEGES = [
    {
        'group': 'Menu',
        'text': u'可见菜单',
        'privileges': [
            {
                'name': 'Operation',
                'text': u'运营'
            },
            {
                'name': 'Delivery',
                'text': u'配送'
            },
            {
                'name': 'ClientService',
                'text': u'客服'
            },
            {
                'name': 'Finance',
                'text': u'财务'
            },
            {
                'name': 'Team',
                'text': u'团队'
            },
            {
                'name': 'Analysis',
                'text': u'统计'
            }
        ]
    },
    {
        'group': 'OrderManagement',
        'text': u'订单管理',
        'privileges': [
            {
                'name': 'OrderRead',
                'text': u'查看订单'
            },
            {
                'name': 'OrderConfirm',
                'text': u'确认收货'
            },
            {
                'name': 'OrderRefund',
                'text': u'退款'
            },
            {
                'name': 'OrderSend',
                'text': u'配单'
            }
        ]
    },
    {
        'group': 'TaskManagement',
        'text': u'任务管理',
        'privileges': [
            {
                'text': u'查看任务',
                'name': 'TaskRead'
            },
            {
                'text': u'转单',
                'name': 'TaskTransfer'
            }
        ]
    },
    {
        'group': 'CourierManagement',
        'text': u'速递员管理',
        'privileges': [
            {
                'text': u'查看速递员',
                'name': 'CourierRead'
            },
            {
                'text': u'修改速递员',
                'name': 'CourierUpdate'
            },
            {
                'text': u'审核',
                'name': 'CourierVerify'
            },
            {
                'text': u'锁定',
                'name': 'CourierLock'
            },
            {
                'text': u'清算',
                'name': 'CourierClear'
            },
            {
                'text': u'账户查看',
                'name': 'CourierAccountRead'
            },
            {
                'text': u'账户更新',
                'name': 'CourierAccountUpdate'
            }
        ]
    },
    {
        'group': 'BuildingManagement',
        'text': u'楼栋管理',
        'privileges': [
            {
                'text': u'查看楼栋',
                'name': 'BuildingRead'
            },
            {
                'text': u'更新楼栋',
                'name': 'BuildingUpdate'
            }
        ]
    },
    {
        'group': 'ScheduleManagement',
        'text': u'排班管理',
        'privileges': [
            {
                'text': u'查看排班',
                'name': 'ScheduleRead'
            },
            {
                'text': u'修改排班',
                'name': 'ScheduleUpdate'
            }
        ]
    },
    {
        'group': 'WithdrawManagement',
        'text': u'提现管理',
        'privileges': [
            {
                'text': u'查看提现',
                'name': 'WithdrawRead'
            },
            {
                'text': u'处理提现',
                'name': 'WithdrawUpdate'
            }
        ]
    },
    {
        'group': 'ExpenseManagement',
        'text': u'支出管理',
        'privileges': [
            {
                'text': u'查看支出',
                'name': 'ExpendRead'
            },
            {
                'text': u'处理支出',
                'name': 'ExpendUpdate'
            }
        ]
    },
    {
        'group': 'ClientService',
        'text': u'客户服务',
        'privileges': [
            {
                'text': u'验证码查询',
                'name': 'CodeQuery'
            },
            {
                'text': u'安慰红包',
                'name': 'GiveRedpacket'
            }
        ]
    },
    {
        'group': 'SchoolManagement',
        'text': u'校区管理',
        'privileges': [
            {
                'text': u'查看校区',
                'name': 'SchoolRead'
            },
            {
                'text': u'新增校区',
                'name': 'SchoolCreate'
            },
            {
                'text': u'修改校区',
                'name': 'SchoolUpdate'
            },
            {
                'text': u'删除校区',
                'name': 'SchoolDelete'
            }
        ]
    },
    {
        'group': 'RoleManagement',
        'text': u'角色管理',
        'privileges': [
            {
                'text': u'查看角色',
                'name': 'RoleRead'
            },
            {
                'text': u'新增角色',
                'name': 'RoleCreate'
            },
            {
                'text': u'修改角色',
                'name': 'RoleUpdate'
            },
            {
                'text': u'删除角色',
                'name': 'RoleDelete'
            }
        ]
    },
    {
        'group': 'UserManagement',
        'text': u'人员管理',
        'privileges': [
            {
                'text': u'查看人员',
                'name': 'UserRead'
            },
            {
                'text': u'新增人员',
                'name': 'UserCreate'
            },
            {
                'text': u'修改人员',
                'name': 'UserUpdate'
            },
            {
                'text': u'删除人员',
                'name': 'UserDelete'
            }
        ]
    },
    {
        'group': 'ShopManagement',
        'text': u'店铺管理',
        'privileges': [
            {
                'text': u'查看店铺',
                'name': 'ShopRead'
            },
            {
                'text': u'新增店铺',
                'name': 'ShopCreate'
            },
            {
                'text': u'修改店铺',
                'name': 'ShopUpdate'
            },
            {
                'text': u'删除店铺',
                'name': 'ShopDelete'
            },
            {
                'text': u'查看非便利店商品',
                'name': 'ShopItemRead'
            },
            {
                'text': u'修改非便利店商品',
                'name': 'ShopItemUpdate'
            }
        ]
    },
    {
        'group': 'ItemManagement',
        'text': u'商品管理',
        'privileges': [
            {
                'text': u'查看商品',
                'name': 'ItemRead'
            },
            {
                'text': u'新增商品',
                'name': 'ItemCreate'
            },
            {
                'text': u'修改商品',
                'name': 'ItemUpdate'
            },
            {
                'text': u'删除商品',
                'name': 'ItemDelete'
            }
        ]
    },
    {
        'group': 'Analysis',
        'text': u'统计',
        'privileges': [
            {
                'text': u'查看统计',
                'name': 'AnalysisRead'
            }
        ]
    }
]

