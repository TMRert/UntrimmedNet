import argparse
import fnmatch
import glob
import os
import os.path as osp
import pathlib


def parse_splits(split_path, delimiter=','):
    def line2rec(line):
        items = line.strip().split(delimiter)
        vid = items[0]
        label = items[1]
        return vid, label

    splits = []
    directory = os.fsencode(split_path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("train") and filename.endswith(".txt"):
            split_ix = int(filename.split('.')[0][-2:])
            test_filename = "testlist{:02d}.txt".format(split_ix)
            train_list = [line2rec(x) for x in open(osp.join(split_path, filename))]
            test_list = [line2rec(x) for x in open(osp.join(split_path, test_filename))]
            splits.append((train_list, test_list))
    return splits


def parse_directory(path, key_func=lambda x: x[-11:],
                    rgb_prefix='img_',
                    flow_x_prefix='flow_x_',
                    flow_y_prefix='flow_y_',
                    level=1):
    """
    Parse directories holding extracted frames from standard benchmarks
    """
    print('parse frames under folder {}'.format(path))
    if level == 1:
        frame_folders = glob.glob(osp.join(path, '*'))
    elif level == 2:
        frame_folders = glob.glob(osp.join(path, '*', '*'))
    else:
        raise ValueError('level can be only 1 or 2')

    def count_files(directory, prefix_list):
        lst = os.listdir(directory)
        cnt_list = [len(fnmatch.filter(lst, x + '*')) for x in prefix_list]
        return cnt_list

    # check RGB
    frame_dict = {}
    for i, f in enumerate(frame_folders):
        all_cnt = count_files(f, (rgb_prefix, flow_x_prefix, flow_y_prefix))
        k = key_func(f)

        x_cnt = all_cnt[1]
        y_cnt = all_cnt[2]
        if x_cnt != y_cnt:
            raise ValueError(
                'x and y direction have different number '
                'of flow images. video: ' + f)
        if i % 200 == 0:
            print('{} videos parsed'.format(i))

        frame_dict[k] = (f, all_cnt[0], x_cnt)

    print('frame folder analysis done')
    return frame_dict


def parse_args():
    parser = argparse.ArgumentParser(description='Build file list')
    parser.add_argument('dataset_name', type=str)
    parser.add_argument('db_root', type=str, help='root directory for the frames')
    parser.add_argument('split_list_path', type=str, help='root directory for the split definition files')
    parser.add_argument('--rgb_prefix', type=str, default='image_')
    parser.add_argument('--flow_x_prefix', type=str, default='flow_x_')
    parser.add_argument('--flow_y_prefix', type=str, default='flow_y_')
    parser.add_argument('--subset', type=str, default='train',
                        choices=['train', 'val', 'test'])
    parser.add_argument('--level', type=int, default=2, choices=[1, 2])
    parser.add_argument('--format', type=str,
                        default='rawframes', choices=['rawframes', 'videos'])
    parser.add_argument('--out_list_path', type=str, default='data/')
    parser.add_argument('--shuffle', action='store_true', default=False)
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    if args.level == 2:
        def key_func(x):
            return '/'.join(x.split('/')[-2:])
    else:
        def key_func(x):
            return osp.basename(x)

    if args.format == 'rawframes':
        frame_info = parse_directory(osp.join(osp.abspath(args.db_root)),
                                     key_func=key_func,
                                     rgb_prefix=args.rgb_prefix,
                                     flow_x_prefix=args.flow_x_prefix,
                                     flow_y_prefix=args.flow_y_prefix,
                                     level=args.level)
    else:
        if args.level == 1:
            video_list = glob.glob(osp.join(args.db_root, 'frames', '*'))
        elif args.level == 2:
            video_list = glob.glob(osp.join(args.db_root, 'frames', '*', '*'))
        else:
            raise ValueError("Level can either be 1 or 2")

        frame_info = {osp.relpath(
            x.split('.')[0], args.db_root): (x, -1, -1) for x in video_list}

    split_tp = parse_splits(args.split_list_path, ',')
    out_path = args.out_list_path
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)

    for j, frame_type in enumerate(['rgb', 'flow']):
        for i, split in enumerate(split_tp):
            train_items, test_items = split
            with open(osp.join(out_path, "{}_train_split_{:02d}.txt".format(frame_type, i + 1)), 'w') as train_f:
                for train_item in train_items:
                    video_name = osp.basename(train_item[0])
                    entry_info = frame_info[video_name]
                    train_entry = "%s %s %s\n" % (entry_info[0], entry_info[j + 1], train_item[1])
                    train_f.write(train_entry)

            with open(osp.join(out_path, "{}_test_split_{:02d}.txt".format(frame_type, i + 1)), 'w') as test_f:
                for test_item in test_items:
                    video_name = osp.basename(test_item[0])
                    entry_info = frame_info[video_name]
                    test_entry = "%s %s %s\n" % (entry_info[0], entry_info[j + 1], test_item[1])
                    test_f.write(test_entry)


if __name__ == "__main__":
    main()
