r"""
与地理有关的功能。
"""

import math

# 平均地球半径，取 6371 千米
EARTH_RADIUS = 6371e3


def degrees_to_meters(lat1, lon1, lat2, lon2):
    r"""
    根据地球上两个点的经纬度坐标，计算并返回这两个点在纬度和经度方向上的距离（米）。

    ## 参数

    - `lat1`（`float`）：第一个点的纬度。
    - `lon1`（`float`）：第一个点的经度。
    - `lat2`（`float`）：第二个点的纬度。
    - `lon2`（`float`）：第二个点的经度。

    ## 返回

    - `(float, float)`: 一个包含两个元素的元组，
      - 第一个元素是两点间纬度方向的距离，单位为米。
      - 第二个元素是两点间经度方向的距离，单位为米。

    ## 注意

    - 地球被视为理想球体，使用平均地球半径进行计算。
    - 经度方向的实际距离会根据所在纬度位置有所变化，这里取较小的经度距离变化，而不是平均的。
    """

    # 将角度转换成弧度
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)

    # 计算纬度的差异，单位为弧度
    delta_lat_rad = abs(lat1_rad - lat2_rad)

    # 计算经度的差异，单位为弧度
    delta_lon_rad = abs(lon1_rad - lon2_rad)
    delta_lon_rad = min(delta_lon_rad, math.pi * 2 - delta_lon_rad) # 超过 π 就取其补角

    # 计算纬度方向上的差异，单位为米
    delta_lat_meter = delta_lat_rad * EARTH_RADIUS

    # 计算经度方向上的差异，是较大的纬度上的那个经度差异，因为这个经度差异较小
    delta_lon_meter = delta_lon_rad * EARTH_RADIUS * math.cos(max(abs(lat1_rad), abs(lat2_rad)))

    return (delta_lat_meter, delta_lon_meter)


if __name__ == '__main__':
    # 示例调用
    lat1, lon1 = 40.7128, -74.0060  # 纽约市
    lat2, lon2 = 34.0522, -118.2437 # 洛杉矶
    delta_lat, delta_lon = degrees_to_meters(lat1, lon1, lat2, lon2)
    print(f"纬度方向的距离: {delta_lat:.2f} 米")
    print(f"经度方向的距离: {delta_lon:.2f} 米")
