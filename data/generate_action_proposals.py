import argparse
import os
import pathlib


def segment_video(segment_size, video_size, output_filename):
    with open(output_filename, 'w') as write_f:
        for value in range(1, video_size, segment_size):
            write_f.write("%i\n" % value)


def parse_split(train_def, test_def, outpath, segment_size, split_suffix):
    train_out_dir = os.path.join(outpath, 'train_window_shot_split_{:02d}'.format(split_suffix))
    test_out_dir = os.path.join(outpath, 'test_window_shot_split_{:02d}'.format(split_suffix))
    pathlib.Path(train_out_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(test_out_dir).mkdir(parents=True, exist_ok=True)

    def parse_videofile_line(entry):
        splits = entry.split(' ')
        frames = int(splits[-2])
        path = ''.join(splits[0:-2])
        filename = os.path.basename(path)
        return filename, frames

    def line_to_file(input_file: str, output_path: str, type: str):
        with open(input_file) as input_f:
            shotlist_file = os.path.join(os.path.dirname(train_def),
                                         '{}_shot_list_split_{:02d}.txt'.format(type, split_suffix))
            with open(shotlist_file, 'w') as shot_f:
                for line in input_f:
                    video_filename, nr_frames = parse_videofile_line(line)
                    output_filename = os.path.join(output_path, "%s_window_shot.txt" % video_filename)
                    segment_video(segment_size, nr_frames, output_filename)
                    shot_f.write("{} {}\n".format(os.path.abspath(output_filename), nr_frames))

    line_to_file(train_def, train_out_dir, 'train')
    line_to_file(test_def, test_out_dir, 'test')
    return


def parse_args():
    parser = argparse.ArgumentParser(description='Build uniformly split action proposals')
    parser.add_argument('split_list_path', type=str, help='root directory for the split definition files')
    parser.add_argument('--out_dir', type=str, default='data/')
    parser.add_argument('--segment_size', type=int, default=300)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    directory = os.fsencode(args.split_list_path)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("rgb_train") and filename.endswith(".txt"):
            split_ix = int(filename.split('.')[0][-2:])
            test_filename = "rgb_test_split_{:02d}.txt".format(split_ix)

            path_to_train = os.path.join(args.split_list_path, filename)
            path_to_test = os.path.join(args.split_list_path, test_filename)
            parse_split(path_to_train, path_to_test, args.out_dir, args.segment_size, split_ix)


if __name__ == '__main__':
    main()
