#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import AuthenticationError, TimeoutError

from common.log import log
from core.conf import settings


class RedisCli(Redis):
    def __init__(self):
        # 创建连接池
        pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            decode_responses=True,  # 转码 utf-8
            max_connections=settings.REDIS_MAX_CONNECTIONS,  # 可选，设置连接池中的最大连接数
            socket_timeout=settings.REDIS_TIMEOUT,  # 可选，设置socket超时时间
        )

        # 使用连接池创建Redis客户端实例
        super().__init__(connection_pool=pool)

    async def open(self):
        """
        触发初始化连接（实际上，使用连接池后，初始化连接在需要时自动进行）
        但为了保持接口的一致性，我们还是保留这个方法，并在其中进行ping操作以测试连接。
        """
        try:
            await self.ping()
        except TimeoutError:
            log.error('❌ 数据库 redis 连接超时')
            sys.exit()
        except AuthenticationError:
            log.error('❌ 数据库 redis 连接认证失败')
            sys.exit()
        except Exception as e:
            log.error('❌ 数据库 redis 连接异常 {}', e)
            sys.exit()

    async def delete_prefix(self, prefix: str, exclude: str | list = None):
        """
        删除指定前缀的所有key

        :param prefix: 前缀
        :param exclude: 需要排除的key或key列表
        """
        keys = []
        async for key in self.scan_iter(match=f'{prefix}*'):
            if isinstance(exclude, str):
                if key != exclude:
                    keys.append(key)
            elif isinstance(exclude, list):
                if key not in exclude:
                    keys.append(key)
            else:
                keys.append(key)
        if keys:
            await self.delete(*keys)


# 创建 redis 客户端实例
redis_client = RedisCli()
