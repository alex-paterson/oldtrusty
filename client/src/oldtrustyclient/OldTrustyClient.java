/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;

import java.io.IOException;
import java.net.UnknownHostException;
import java.util.logging.Level;
import java.util.logging.Logger;
import net.sourceforge.argparse4j.inf.ArgumentParserException;

/**
 *
 * @author Owner
 */
public class OldTrustyClient {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
         
        ArgParser argParser = null;
        ArgParser.ArgumentStruct argStruct = null;
        try {
            argParser = new ArgParser();
            argStruct = argParser.parse(args);
        } catch (IllegalArgumentException | ArgumentParserException | UnknownHostException e) {
            System.out.printf(e.getLocalizedMessage());
            System.out.printf("\n");
            if(argParser != null) 
                argParser.printHelp();
            return;
        }
        
        
        try {
            TCPClient client = new TCPClient(argStruct);
            client.go();
        } catch (IOException ex) {
            System.out.printf(ex.getLocalizedMessage());
            System.out.printf("\n");
        }
    }
    
}
