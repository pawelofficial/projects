from torch import nn, optim
import torch 
import pandas as pd 
import random 
from torch.utils.data import DataLoader
from torch.utils.data import Dataset

class Network(nn.Module):
    def __init__(self, input_features, output_features, scale_factor):
        super(Network, self).__init__()

        layers = []
        in_features = input_features
        while in_features > output_features*scale_factor:
            out_features = max(int(in_features/scale_factor), output_features*scale_factor)
            layers.append(nn.Linear(in_features, out_features))
            layers.append(nn.ReLU())
            in_features = out_features

        layers.append(nn.Linear(in_features, output_features))
        self.layers = nn.Sequential(*layers)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.layers(x)
        x = self.sigmoid(x)
        return x
    
    


class MyDataset(Dataset):
    def __init__(self, df, feature_columns, label_columns):
        self.features = df[feature_columns].values.astype('float32')
        self.labels = df[label_columns].values.astype('float32')
        # cast features ad labels to float32


    def __getitem__(self, index):
        return self.features[index], self.labels[index]

    def __len__(self):
        return len(self.features)


# Assuming the Network class is defined here
N_features=10
N_labels=1
random_list= lambda :[random.randint(0,100)/100 for i in range(N_features)]
features_dic={f'feature_{i}':random_list() for i in range(N_features)}
labels_dic={f'label_{i}':random_list() for i in range(N_labels)}
df=pd.DataFrame({**features_dic,**labels_dic})
feature_columns=[f'feature_{i}' for i in range(N_features)]
label_columns=[f'label_{i}' for i in range(N_labels)]

# Create an instance of Network
net = Network(input_features=10, output_features=1, scale_factor=2)
dataset=MyDataset(df, feature_columns, label_columns)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Define a loss function and an optimizer
criterion = nn.MSELoss()
optimizer = optim.SGD(net.parameters(), lr=0.01)

# Generate synthetic data
# For simplicity, we'll generate random tensors for inputs and targets
inputs = torch.randn(100, 10)  # 100 samples, each with 10 features
inputs=torch.tensor(df[feature_columns].values).to(torch.float32)
targets = torch.randn(100, 1)  # 100 targets, each with 1 value
targets=torch.tensor(df[label_columns].values).to(torch.float32)
# cast inputs and targets to float32 



# Training loop
###for epoch in range(100):  # 100 epochs
###    # Forward pass: compute predicted outputs by passing inputs to the model
###    outputs = net(inputs)
###    # Compute loss
###    loss = criterion(outputs, targets)
###    # Zero gradients, perform a backward pass, and update the weights
###    optimizer.zero_grad()
###    loss.backward()
###    optimizer.step()
###    # Print loss every 10 epochs
###    if epoch % 10 == 0:
###        print(f'Epoch {epoch}, Loss: {loss.item()}')
        
        
num_epochs=100
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Training loop
for epoch in range(num_epochs):
    for i, (inputs, labels) in enumerate(dataloader):
        # Move inputs and labels to the target device
        inputs, labels = inputs.to(device), labels.to(device)

        # Forward pass
        outputs = net(inputs).to(torch.float32)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print(f'Epoch {epoch}, Loss: {loss.item()}')
        
torch.save(net.state_dict(), 'model.pth')