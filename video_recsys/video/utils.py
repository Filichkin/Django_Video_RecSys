import warnings

from decouple import config
import torch
from torchvision import models
from torchvision.io.video import read_video


warnings.filterwarnings('ignore')

r2plus1d_18 = models.video.R2Plus1D_18_Weights.DEFAULT
transform_default = r2plus1d_18.transforms()
weights = torch.load(config('WEIGHTS_PATH'))
model = models.video.r2plus1d_18(weights)
model.load_state_dict(weights)


def get_embedding(video, model=model, transform_default=transform_default):
    layer = model._modules.get('avgpool')
    outputs = []

    def copy_embeddings(module, input, output):
        output = output[:, :, 0, 0].detach().numpy().tolist()
        outputs.append(output)

    tensor = layer.register_forward_hook(copy_embeddings)
    vid, _, _ = read_video(
        video,
        output_format='TCHW'
        )
    vid = vid[:32]
    batch = transform_default(vid).unsqueeze(0)
    model.eval()
    tensor = model(batch)
    embeddings = outputs[0][0]
    list_embeddings = [item for sublist in embeddings for item in sublist]

    return list_embeddings
