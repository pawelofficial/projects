from torch import nn, optim
import torch 
import pandas as pd 
import random 
from torch.utils.data import DataLoader
from torch.utils.data import Dataset

###class Network(nn.Module):
###    def __init__(self, input_features, output_features, scale_factor):
###        super(Network, self).__init__()
###
###        layers = []
###        in_features = input_features
###        while in_features > output_features*scale_factor:
###            out_features = max(int(in_features/scale_factor), output_features*scale_factor)
###            layers.append(nn.Linear(in_features, out_features))
###            layers.append(nn.ReLU())
###
###            in_features = out_features
###
###        layers.append(nn.Linear(in_features, output_features))
###        self.layers = nn.Sequential(*layers)
###        self.sigmoid = nn.Sigmoid()
###
###    def forward(self, x):
###        x = self.layers(x)
###        x = self.sigmoid(x)
###        return x
import torch.nn.functional as F
class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.layer1 = nn.Linear(4, 10)  # First hidden layer with 10 neurons
        self.layer2 = nn.Linear(10, 10)  # Second hidden layer with 10 neurons
        self.layer3 = nn.Linear(10, 10)  # Third hidden layer with 10 neurons
        self.layer4 = nn.Linear(10, 1)  # Output layer with 1 neuron

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        x = self.layer4(x)  # No activation function is used for the output layer in binary classification
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
df=pd.read_csv('./iris.csv')
label_columns=['species']
feature_columns=[i for i in df.columns if i not in label_columns]

# scale feature columns 
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df[feature_columns] = scaler.fit_transform(df[feature_columns])



# Create an instance of Network
#net = Network(input_features=4, output_features=1, scale_factor=2)
net=Network()
dataset=MyDataset(df, feature_columns, label_columns)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

# Define a loss function and an optimizer
criterion = nn.MSELoss()
criterion=nn.CrossEntropyLoss()
#optimizer = optim.SGD(net.parameters(), lr=0.01)
optimizer=optim.Adam(net.parameters(), lr=0.0001)

        
num_epochs=100
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Training loop
for epoch in range(num_epochs):
    for i, (inputs, labels) in enumerate(dataloader):
        # Move inputs and labels to the target device
        inputs, labels = inputs.to(device), labels.to(device)
#        print(inputs)
#        print('------------------')
#        print(labels)
#        input('wait')
        # Forward pass
        outputs = net(inputs).to(torch.float32)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print(f'Epoch {epoch}, Loss: {loss.item()}')
        
torch.save(net.state_dict(), 'model.pth')


# Evaluation loop
net.eval()  # Set the model to evaluation mode
with torch.no_grad():  # Disable gradient computation
    correct = 0
    total = 0
    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = net(inputs)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print(f'Accuracy of the model on the test data: {accuracy}%')