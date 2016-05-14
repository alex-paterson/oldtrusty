/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;
import java.net.InetAddress;
import java.net.UnknownHostException;
/**
 *
 * @author Owner
 */
public class ArgumentParser {
    
    public enum Mode {
           upload,
           download;
       };
    
    public class Arguments {
        Mode mode;
        
        String uploadFileName;
        String downloadFileName;
        InetAddress hostIP;
        int hostPort;
    }
    
    public Arguments parse(String[] args) throws UnknownHostException
    {
        Arguments argStruct = new Arguments();

        for (int i = 0; i < args.length; i++) {
            switch (args[i].charAt(0)) {
                case '-':
                    if (args[i].length() != 2) {
                        throw new IllegalArgumentException("Not a valid argument: " + args[i]);
                    }
                    
                    if (args[i].charAt(1) == '-') {
                            throw new IllegalArgumentException("Not a valid argument: " + args[i]);
                            
                    } else {
                        i = doOption(argStruct, args, i);
                    }
                    break;
            }
        }
        
        return argStruct;
    }
        
    private int doOption(Arguments argStruct, String[] args, int index) throws UnknownHostException
    {
        if(args.length - index < 2)
            throw new IllegalArgumentException("Expected arg after: " + args[index]);
        
        switch(args[index].charAt(1))
        {
            case 'a':
                //assume upload
                argStruct.mode = Mode.upload;
                argStruct.uploadFileName = args[index+1];
                index++;
                break;
            case 'f':
                argStruct.mode = Mode.download;
                argStruct.downloadFileName = args[index+1];
                index++;
                break;
            case 'h':
                String[] ip = args[index+1].split(":", 2);
                
                if(ip.length != 2)
                    throw new IllegalArgumentException("Need host port");
                
                argStruct.hostIP = InetAddress.getByName(ip[0]);
                argStruct.hostPort = java.lang.Integer.getInteger(ip[1], 3002);
                break;
        }
        return index;
    }
}
