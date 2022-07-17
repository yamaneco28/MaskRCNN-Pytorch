import os
import urllib.request

import mmcv
from mmrotate.models import build_detector
from mmcv.runner import load_checkpoint

# KLD
# default_config_path = '../mmrotate/configs/rotated_retinanet/rotated_retinanet_obb_r50_fpn_1x_dota_le90.py'
# default_checkpoint_path = 'rotated_retinanet/rotated_retinanet_obb_r50_fpn_1x_dota_le90/rotated_retinanet_obb_r50_fpn_1x_dota_le90-c0097bc4.pth'

# ReDet
# default_config_path = '../mmrotate/configs/redet/redet_re50_refpn_1x_dota_ms_rr_le90.py'
# default_checkpoint_path = 'redet/redet_re50_fpn_1x_dota_ms_rr_le90/redet_re50_fpn_1x_dota_ms_rr_le90-fc9217b5.pth'

# KFIoU
default_config_path = '../mmrotate/configs/rotated_retinanet/rotated_retinanet_hbb_r50_fpn_1x_dota_oc.py'
default_checkpoint_path = 'rotated_retinanet/rotated_retinanet_hbb_r50_fpn_1x_dota_oc/rotated_retinanet_hbb_r50_fpn_1x_dota_oc-e8a7c7df.pth'


def get_model_MMRotate(
    config_path: str = default_config_path,
    checkpoint_path: str = default_checkpoint_path,
    device: str = 'cuda',
    pretrained: bool = None,
):
    MMRotateModel_path = 'MMRotateModels/'

    # download model params if it doesn't exist
    checkpoint_save_path = os.path.join(MMRotateModel_path, checkpoint_path)
    if not os.path.exists(checkpoint_save_path):
        base_url = 'https://download.openmmlab.com/mmrotate/v0.1.0/'
        download_path = base_url + checkpoint_path
        print(f'Downloading checkpoint from {download_path}')

        # make directory if it doesn't exist
        dirname = os.path.dirname(checkpoint_save_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        urllib.request.urlretrieve(download_path, checkpoint_save_path)

    print('load config from local path:', config_path)
    config = mmcv.Config.fromfile(config_path)
    config.model.pretrained = pretrained
    model = build_detector(config.model)
    model.to(device)

    checkpoint = load_checkpoint(
        model, checkpoint_save_path, map_location=device)
    model.CLASSES = checkpoint['meta']['CLASSES']
    model.cfg = config

    return model


def argparse():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--image', type=str,
                        default='../mmrotate/demo/demo.jpg')
    parser.add_argument('--output', type=str,
                        default='./results/MMRotate_demo_result.jpg')
    parser.add_argument('--epoch', type=int, default=10000)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--learning_rate', type=float, default=0.001)
    parser.add_argument('--gpu', default='0',
                        type=lambda x: list(map(int, x.split(','))))
    args = parser.parse_args()
    return args


def main(args):
    model = get_model_MMRotate()
    # print(model)
    print('Classes:', model.CLASSES)

    # Inference
    # img = '../mmrotate/demo/demo.jpg'
    import mmdet.apis
    import time
    start = time.time()
    result = mmdet.apis.inference_detector(model, args.image)
    end = time.time()
    print(f'Inference time: {end - start:.6f} [s]')

    # 結果の表示
    mmdet.apis.show_result_pyplot(
        model,
        args.image,
        result,
        score_thr=0.3,
        palette='dota',
        out_file=args.output,
    )


if __name__ == '__main__':
    args = argparse()
    main(args)
