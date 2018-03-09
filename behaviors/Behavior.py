#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


from base.Loader import ModelLoaderSingleton
import settings
import logging


class Behavior(object):
    def __init__(self):
        super(Behavior, self).__init__()
        self._loader = ModelLoaderSingleton()

    @property
    def bill_model(self):
        return self._loader.Use("BillModel")

    @property
    def courier_model(self):
        return self._loader.Use("CourierModel")

    @property
    def image_model(self):
        return self._loader.Use("ImageModel")

    @property
    def school_model(self):
        return self._loader.Use("SchoolModel")

    @property
    def subtask_model(self):
        return self._loader.Use("SubtaskModel")

    @property
    def task_model(self):
        return self._loader.Use('TaskModel')

    @property
    def withdraw_model(self):
        return self._loader.Use("WithdrawModel")

    @property
    def fine_model(self):
        return self._loader.Use("FineModel")

    @property
    def expend_model(self):
        return self._loader.Use("ExpendModel")

    @property
    def income_model(self):
        return self._loader.Use("IncomeModel")

    @property
    def location_model(self):
        return self._loader.Use("LocationModel")

    @property
    def branches_model(self):
        return self._loader.Use("BranchesModel")

    @property
    def open_user_model(self):
        return self._loader.Use("OpenUserModel")

    @property
    def console_user_model(self):
        return self._loader.Use("ConsoleUserModel")

    @property
    def schedule_model(self):
        return self._loader.Use('ScheduleModel')

    @property
    def shop_model(self):
        return self._loader.Use("ShopModel")

    @property
    def category_model(self):
        return self._loader.Use("CategoryModel")

    @property
    def coupon_model(self):
        return self._loader.Use("CouponModel")

    @property
    def item_model(self):
        return self._loader.Use("ItemModel")

    @property
    def order_model(self):
        return self._loader.Use("OrderModel")

    @property
    def pay_model(self):
        return self._loader.Use("PayModel")

    @property
    def shop_model(self):
        return self._loader.Use("ShopModel")

    @property
    def user_model(self):
        return self._loader.Use("UserModel")

    @property
    def feedback_model(self):
        return self._loader.Use("FeedbackModel")

    @property
    def activity_model(self):
        return self._loader.Use("ActivityModel")

    @property
    def role_model(self):
        return self._loader.Use("RoleModel")

    @property
    def item_repo_model(self):
        return self._loader.Use("ItemRepoModel")

    @property
    def building_model(self):
        return self._loader.Use("BuildingModel")

    @property
    def region_model(self):
        return self._loader.Use("RegionModel")

    @property
    def order_statistics(self):
        return self._loader.Use("OrderStatisticsModel")

    @property
    def user_statistics(self):
        return self._loader.Use("UserStatisticsModel")

    @property
    def order_refund_model(self):
        return self._loader.Use("OrderRefundModel")

    @property
    def order_hurry_model(self):
        return self._loader.Use("OrderHurryModel")

    @property
    def async_redis(self):
        return self._loader.Use(settings.redis.DATA_CACHE_KEY)

    @property
    def shark_redis(self):
        logging.debug(self._loader.Use(settings.redis.SHARK_CACHE_KEY))
        return self._loader.Use(settings.redis.SHARK_CACHE_KEY)

    @property
    def wukong_redis(self):
        return self._loader.Use(settings.redis.WUKONG_CACHE_KEY)

    @property
    def queue(self):
        return self._loader.Use(settings.redis.RQ_CACHE_KEY)
