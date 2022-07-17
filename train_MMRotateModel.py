import os
import time

from mmrotate.datasets.builder import ROTATED_DATASETS
from mmrotate.datasets.dota import DOTADataset
import mmcv
import mmdet
import mmdet.apis

config_path = '../mmrotate/configs/rotated_retinanet/rotated_retinanet_obb_r50_fpn_1x_dota_le90.py'
checkpoint_path = './MMRotateModels/rotated_retinanet/rotated_retinanet_obb_r50_fpn_1x_dota_le90/rotated_retinanet_obb_r50_fpn_1x_dota_le90-c0097bc4.pth'


@ROTATED_DATASETS.register_module()
class TinyDataset(DOTADataset):
    CLASSES = ('ship',)


def main(args):
    config = mmcv.Config.fromfile(config_path)

    data_path = './data/ssdd_tiny/'

    config.dataset_type = 'TinyDataset'
    config.data_root = args.data

    # test
    config.data.test.type = 'TinyDataset'
    config.data.test.data_root = data_path
    config.data.test.ann_file = 'val'
    config.data.test.img_prefix = 'images'

    # train
    config.data.train.type = 'TinyDataset'
    config.data.train.data_root = data_path
    config.data.train.ann_file = 'train'
    config.data.train.img_prefix = 'images'

    # val
    config.data.val.type = 'TinyDataset'
    config.data.val.data_root = data_path
    config.data.val.ann_file = 'val'
    config.data.val.img_prefix = 'images'

    # class num
    # config.model.roi_head.bbox_head[0].num_classes = 1
    # config.model.roi_head.bbox_head[1].num_classes = 1

    # model path
    config.load_from = checkpoint_path

    # output path
    config.work_dir = args.output

    # learning rate
    config.optimizer.lr = args.learning_rate
    # epoch
    config.runner.max_epochs = args.epoch

    # seed
    SEED = 12
    config.seed = SEED
    mmdet.apis.set_random_seed(SEED, deterministic=False)

    # device setting
    # config.device = f'cuda:{args.gpu[0]}'
    config.device = 'cuda'
    config.gpu_ids = args.gpu

    # log setting
    config.log_config.interval = 10
    config.log_config.hooks = [
        dict(type='TextLoggerHook'),
    ]

    # make dataset
    datasets = [mmdet.datasets.build_dataset(config.data.train)]

    # make model
    model_for_train = mmdet.models.build_detector(
        config.model,
        train_cfg=config.get('train_cfg'),
        test_cfg=config.get('test_cfg'),
    )

    # classes setting
    model_for_train.CLASSES = datasets[0].CLASSES

    # make output dir
    mmcv.mkdir_or_exist(os.path.abspath(config.work_dir))

    print(config.pretty_text)

    # train
    start = time.time()
    mmdet.apis.train_detector(
        model_for_train,
        datasets,
        config,
        distributed=False,
        validate=True,
    )
    end = time.time()
    print(f'Training time: {end - start:%2f} sec')


def argparse():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--data', type=str, default='./data/ssdd_tiny/')
    parser.add_argument('--output', type=str,
                        default='./results/MMRotate_test/')
    parser.add_argument('--epoch', type=int, default=10000)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--learning_rate', type=float, default=0.001)
    parser.add_argument('--gpu', default='0',
                        type=lambda x: list(map(int, x.split(','))))
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = argparse()
    main(args)