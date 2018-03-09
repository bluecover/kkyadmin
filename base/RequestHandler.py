#!/usr/bin/env python
# encoding=UTF8
__author__ = 'paul'
__date__ = '2015-01-22 16:53:40'

import tornado.web
import settings

class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(RequestHandler, self).__init__(*args, **kwargs)

    @property
    def async_redis(self):
        return self.application._async_redis

    @property
    def shark_redis(self):
        return self.application._loader.Use(settings.redis.SHARK_CACHE_KEY)

    @property
    def wukong_redis(self):
        return self.application._loader.Use(settings.redis.WUKONG_CACHE_KEY)

    @property
    def queue(self):
        return self.application._loader.Use(settings.redis.RQ_CACHE_KEY)

    @property
    def bill_model(self):
        return self.application._loader.Use("BillModel")

    @property
    def courier_model(self):
        return self.application._loader.Use("CourierModel")

    @property
    def image_model(self):
        return self.application._loader.Use("ImageModel")

    @property
    def school_model(self):
        return self.application._loader.Use("SchoolModel")

    @property
    def subtask_model(self):
        return self.application._loader.Use("SubtaskModel")

    @property
    def task_model(self):
        return self.application._loader.Use('TaskModel')

    @property
    def withdraw_model(self):
        return self.application._loader.Use("WithdrawModel")

    @property
    def income_model(self):
        return self.application._loader.Use("IncomeModel")

    @property
    def location_model(self):
        return self.application._loader.Use("LocationModel")

    @property
    def branches_model(self):
        return self.application._loader.Use("BranchesModel")

    @property
    def open_user_model(self):
        return self.application._loader.Use("OpenUserModel")

    @property
    def console_user_model(self):
        return self.application._loader.Use("ConsoleUserModel")

    @property
    def schedule_model(self):
        return self.application._loader.Use('ScheduleModel')

    @property
    def shop_model(self):
        return self.application._loader.Use("ShopModel")

    @property
    def category_model(self):
        return self.application._loader.Use("CategoryModel")

    @property
    def coupon_model(self):
        return self.application._loader.Use("CouponModel")

    @property
    def item_model(self):
        return self.application._loader.Use("ItemModel")

    @property
    def order_model(self):
        return self.application._loader.Use("OrderModel")

    @property
    def pay_model(self):
        return self.application._loader.Use("PayModel")

    @property
    def shop_model(self):
        return self.application._loader.Use("ShopModel")

    @property
    def user_model(self):
        return self.application._loader.Use("UserModel")

    @property
    def feedback_model(self):
        return self.application._loader.Use("FeedbackModel")

    @property
    def activity_model(self):
        return self.application._loader.Use("ActivityModel")

    @property
    def role_model(self):
        return self.application._loader.Use("RoleModel")

    @property
    def item_repo_model(self):
        return self.application._loader.Use("ItemRepoModel")

    @property
    def building_model(self):
        return self.application._loader.Use("BuildingModel")

    @property
    def fine_model(self):
        return self.application._loader.Use("FineModel")

    @property
    def expend_model(self):
        return self.application._loader.Use("ExpendModel")

    @property
    def order_refund_model(self):
        return self.application._loader.Use("OrderRefundModel")

    @property
    def order_hurry_model(self):
        return self.application._loader.Use("OrderHurryModel")
