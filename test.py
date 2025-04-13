import unittest
from utils import serialize

class Tests(unittest.TestCase):

  def test_serialization(self):
    serialization = serialize(
      {'weather_data':
        {'time':
          [
            '2025-04-13',
            '2025-04-14',
            '2025-04-15',
            '2025-04-16',
            '2025-04-17',
            '2025-04-18',
            '2025-04-19'
          ]
        }
      }
    )
    self.assertEqual(
      serialization,
      {'M':
        {"weather_data":
          { 'M':
            {"time":
              {
                "L": [
                  { "S": "2025-04-13" },
                  { "S": "2025-04-14" },
                  { "S": "2025-04-15" },
                  { "S": "2025-04-16" },
                  { "S": "2025-04-17" },
                  { "S": "2025-04-18" },
                  { "S": "2025-04-19" }
                ]
              }
            }
          }
        }
      }, 'The serialization is wrong.')

if __name__ == '__main__':
    unittest.main()