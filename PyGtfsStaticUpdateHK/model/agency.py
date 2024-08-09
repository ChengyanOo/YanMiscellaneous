from enum import Enum

kmb_route_stop_endpoint = 'https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{direction}/1'
ctb_route_stop_endpoint = 'https://rt.data.gov.hk/v2/transport/citybus/route-stop/CTB/{route}/{direction}'

class Agency(Enum):
    MTR = 1
    KMB = 2
    LWB = 3
    CTB = 4
    SUN_FERRY = 6
    HKKF = 7
    NLB = 8
    HK_TRAMWAYS = 10
    STAR_FERRY = 11
    PARK_ISLAND = 13
    NGONG_PING = 14
    DISCOVERY_BAY = 15
    GREEN_MINIBUS = 16
    FORTUNE_FERRY = 17
    CORAL_SEA_FERRY = 18
    BLUE_SEA_FERRY = 19
    TRAWAY_TRAVEL = 20
    CHUEN_KEY_FERRY = 22
    MTR_BUS = 25
    KMB_CITYBUS = 27
    LWB_CITYBUS = 29
    HK_INTERNATIONAL_AIRPORT = 33
    KAITO_FERRY = 34
    PEAK_TRAMWAYS = 9
    HZMB_SHUTTLE_BUS = 30
    SUN_BUS = 39
    WATER_TAXI = 40
    YIM_TIN_TSAI = 41
    CKS = 24
    TURBOJET = 23
    COTAI_WATER_JET = 26

