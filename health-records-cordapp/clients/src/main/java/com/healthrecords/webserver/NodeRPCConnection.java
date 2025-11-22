package com.healthrecords.webserver;

import net.corda.client.rpc.CordaRPCClient;
import net.corda.client.rpc.CordaRPCConnection;
import net.corda.core.messaging.CordaRPCOps;
import net.corda.core.utilities.NetworkHostAndPort;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

@Component
public class NodeRPCConnection implements AutoCloseable {
    
    @Value("${config.rpc.host}")
    private String host;
    
    @Value("${config.rpc.port}")
    private int port;
    
    @Value("${config.rpc.username}")
    private String username;
    
    @Value("${config.rpc.password}")
    private String password;
    
    private CordaRPCConnection rpcConnection;
    
    @PostConstruct
    public void initialiseNodeRPCConnection() {
        NetworkHostAndPort rpcAddress = new NetworkHostAndPort(host, port);
        CordaRPCClient rpcClient = new CordaRPCClient(rpcAddress);
        rpcConnection = rpcClient.start(username, password);
    }
    
    @PreDestroy
    public void close() {
        rpcConnection.notifyServerAndClose();
    }
    
    public CordaRPCOps getProxy() {
        return rpcConnection.getProxy();
    }
}
