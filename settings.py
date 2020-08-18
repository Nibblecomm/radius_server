import sys
import logging

def convert_to_int(value):
    '''Function that will convert to int'''
    return int(value)


def convert_kbps_to_bits(in_kbps):
    '''Function that will convert Kbps to bps. Used in most routers'''
    return int(in_kbps) *1024

def convert_mb_to_bytes(in_mb):
    '''Function that will convert Kbps to bps. Used in most routers'''
    return int(in_mb) *1024 * 1024

vendor_cfg = {
  14988:{ # mikrotik  as per router's perspective, Xmit is towards client
      "speed_ul":{
          'attr':'Ascend-Data-Rate',
          'convertor':convert_kbps_to_bits
      },
      "speed_dl":{
          'attr':'Ascend-Xmit-Rate',
          'convertor':convert_kbps_to_bits
      },
      "dl_data_limit":{
          'attr':'Mikrotik-Recv-Limit',
          'convertor':convert_mb_to_bytes
      },
      "ul_data_limit": {
          'attr': 'Mikrotik-Xmit-Limit',
          'convertor': convert_mb_to_bytes
      }
  },
  14122:{ # OpenMesh  as per router's perspective, Xmit is towards client
      "speed_ul": {
          'attr': 'WISPr-Bandwidth-Max-Up',
          'convertor': convert_kbps_to_bits
      },
      "speed_dl": {
          'attr': 'WISPr-Bandwidth-Max-Down',
          'convertor': convert_kbps_to_bits
      }

  },
14559:{ # Chillispot  as per router's perspective, Xmit is towards client
  "speed_ul": {
      'attr': 'ChilliSpot-Bandwidth-Max-Up'
  },
  "speed_dl": {
      'attr': 'ChilliSpot-Bandwidth-Max-Down'
  },
  "data_limit": {
      'attr': 'ChilliSpot-Max-Total-Octets',
      'convertor': convert_mb_to_bytes
  }
},
    14823:{# set Aruba user ROle
         #
       "user_role":"Aruba-User-Role"
    },
    890: {  # Zyxel  as per router's perspective, Xmit is towards client
        "speed_ul": {
            'attr': 'WISPr-Bandwidth-Max-Up',
            'convertor': convert_kbps_to_bits
        },
        "speed_dl": {
            'attr': 'WISPr-Bandwidth-Max-Down',
            'convertor': convert_kbps_to_bits
        }

    },
} 