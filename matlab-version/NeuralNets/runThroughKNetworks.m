function activations = runThroughKNetworks(networks, states)
    for i = 1:length(networks)
        activations{i} = run_through_network(networks{i}, states);
    end