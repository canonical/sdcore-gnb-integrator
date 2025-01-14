# SD-Core gNB Integrator
[![CharmHub Badge](https://charmhub.io/sdcore-gnb-integrator/badge.svg)](https://charmhub.io/sdcore-gnb-integrator)

An operator charm providing a way to integrate externally managed (not by [Juju][Juju] charms) 
gNodeBs with [Charmed Aether SD-Core][Charmed Aether SD-Core].
Once the SD-Core gNB Integrator is deployed and integrated with the Charmed Aether SD-Core's NMS,
the gNB will become visible in the Graphical User Interface allowing the network operator to
assign the gNB to a NetworkSlice. Once the gNB is assigned to a NetworkSlice, relevant
configuration (PLMN(s) and TAC) for the gNB will be presented in the output of the `juju status`
command.

Example:

```shell
ubuntu@host:~ $ juju status
Model                  Controller          Cloud/Region        Version  SLA          Timestamp
gnb-integrator         microk8s-localhost  microk8s/localhost  3.6.1    unsupported  12:08:45+01:00

App                    Version  Status   Scale  Charm                  Channel      Rev  Address         Exposed  Message
sdcore-gnb-integrator           waiting      1  sdcore-gnb-integrator                 0  10.152.183.99   no       installing agent

Unit                      Workload  Agent  Address       Ports  Message
sdcore-gnb-integrator/0*  active    idle   10.1.194.207         PLMNs: {'mcc': '001', 'mnc': '01', 'sst': 1, 'sd': 1056816}, TAC: 1
```

## Usage
juju deploy sdcore-gnb-integrator --channel 1.5/edge
juju integrate sdcore-gnb-integrator <Charmed Aether SD-Core NMS>

[Juju]: https://juju.is
[Charmed Aether SD-Core]: https://canonical-charmed-aether-sd-core.readthedocs-hosted.com/en/latest/
