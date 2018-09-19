from database import *
import sys


def main(argv):
    if len(argv) < 5:
        return 1
    who_name = argv[0]
    gender = argv[1]
    song_id = int(argv[2])
    difficulty = argv[3]
    ori_record_start_time = argv[4]

    Database.insert_play(who_name, gender, song_id, difficulty, ori_record_start_time)
    return 0


if __name__ == '__main__':
    main(sys.argv[1:])
