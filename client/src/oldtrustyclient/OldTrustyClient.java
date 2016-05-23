/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;

import java.net.UnknownHostException;

/**
 *
 * @author Owner
 */
public class OldTrustyClient {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws UnknownHostException {
        ArgumentParser argParser = new ArgumentParser();
        ArgumentParser.Arguments argStruct = argParser.parse(args);
        
        System.out.printf("Go\n");
        
        TCPClient client = new TCPClient(argStruct);
        client.go();
            
        System.out.printf("Done\n");
    }
    
}
