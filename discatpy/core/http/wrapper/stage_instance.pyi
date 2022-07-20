"""
The MIT License (MIT)

Copyright (c) 2022-present EmreTech

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from typing import Optional

from ...types import EllipsisOr, Snowflake

class StageInstanceEndpointMixin:
    async def get_stage_instance(self, channel_id: Snowflake): ...
    async def create_stage_instance(
        self,
        *,
        channel_id: Snowflake,
        topic: str,
        privacy_level: EllipsisOr[int] = ...,
        send_start_notification: EllipsisOr[bool] = ...,
        reason: Optional[str] = None,
    ): ...
    async def modify_stage_instance(
        self,
        channel_id: Snowflake,
        *,
        topic: EllipsisOr[str] = ...,
        privacy_level: EllipsisOr[int] = ...,
        reason: Optional[str] = None,
    ): ...
    async def delete_stage_instance(
        self, channel_id: Snowflake, *, reason: Optional[str] = None
    ): ...
