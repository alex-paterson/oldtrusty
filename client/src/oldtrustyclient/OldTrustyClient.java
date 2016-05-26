/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;

import java.net.UnknownHostException;
import net.sourceforge.argparse4j.inf.ArgumentParserException;

/**
 *
 * @author Owner
 */
public class OldTrustyClient {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws UnknownHostException, ArgumentParserException {
        ArgParser argParser = new ArgParser();
        ArgParser.ArgumentStruct argStruct = argParser.parse(args);
        
        TCPClient client = new TCPClient(argStruct);
        client.go();
    }
    
}
