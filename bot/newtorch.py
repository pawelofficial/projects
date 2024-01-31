from torch import nn, optim
import torch 
import pytorch as torch 

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
    
    

# Assuming the Network class is defined here

# Create an instance of Network
net = Network(input_features=10, output_features=1, scale_factor=2)

# Define a loss function and an optimizer
criterion = nn.MSELoss()
optimizer = optim.SGD(net.parameters(), lr=0.01)

# Generate synthetic data
# For simplicity, we'll generate random tensors for inputs and targets
inputs = torch.randn(100, 10)  # 100 samples, each with 10 features
targets = torch.randn(100, 1)  # 100 targets, each with 1 value

# Training loop
for epoch in range(100):  # 100 epochs
    # Forward pass: compute predicted outputs by passing inputs to the model
    outputs = net(inputs)

    # Compute loss
    loss = criterion(outputs, targets)

    # Zero gradients, perform a backward pass, and update the weights
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Print loss every 10 epochs
    if epoch % 10 == 0:
        print(f'Epoch {epoch}, Loss: {loss.item()}')
        
        
torch.save(net.state_dict(), 'model.pth')