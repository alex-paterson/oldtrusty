package oldtrustyclient;

import java.io.IOException;
import java.net.UnknownHostException;
import net.sourceforge.argparse4j.inf.ArgumentParserException;

/**
 *
 * Top level of oldTrustClient
 */
public class OldTrustyClient {

    /**
     * Runs oldTrusty client
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
        } catch (IOException | ClassNotFoundException ex) {
            System.out.printf(ex.getLocalizedMessage());
            System.out.printf("\n");
        }
    }
    
}
