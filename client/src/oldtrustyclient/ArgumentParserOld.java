/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;
/**
 *
 * @author Owner
 */
public class ArgumentParserOld {
    
    public enum Mode {
        unset,
        upload,
        download,
        vouch,
        listFiles,
        uploadCertificate;
       };
    
    public class Arguments {
        Mode mode;
        
        String uploadFileName;
        String downloadFileName;
        String fileToVouch;
        
        InetAddress hostIP;
        int hostPort;
        
        List<String> namesToInclude;
        int circleCircumference;
    }
    
    Arguments argStruct;
    
    public ArgumentParserOld() throws UnknownHostException
    {
        argStruct = new Arguments();
        
        //Setting defaults
        argStruct.circleCircumference = 1;
        argStruct.mode = Mode.unset;
        argStruct.hostIP = InetAddress.getByName("192.168.0.132");
        argStruct.hostPort = 3002;
        
        argStruct.namesToInclude = new ArrayList<>();
    }
    
    public Arguments parse(String[] args) throws UnknownHostException
    {
        Arguments argStruct = new Arguments();

        for (int i = 0; i < args.length;) {
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
    
    private void checkIfOption()
    {
        if(argStruct.mode != Mode.unset)
        {
            throw new IllegalArgumentException("Invalid argument combination");
        }        
    }
        
    private int doOption(Arguments argStruct, String[] args, int index) throws UnknownHostException
    {
        if(args.length - index < 2)
            throw new IllegalArgumentException("Expected arg after: " + args[index]);
        
        switch(args[index].charAt(1))
        {
            case 'a':
                //assume upload
                checkIfOption();
                argStruct.mode = Mode.upload;
                argStruct.uploadFileName = args[++index];
                index++;
                break;
            case 'f':
                checkIfOption();
                argStruct.mode = Mode.download;
                argStruct.downloadFileName = args[++index];
                index++;
                break;                
            case 'u':
                checkIfOption();
                argStruct.mode = Mode.uploadCertificate;
                argStruct.uploadFileName = args[++index];
                index++;
                break;
            case 'v':
                checkIfOption();
                argStruct.mode = Mode.vouch;
                argStruct.fileToVouch = args[++index];
                argStruct.uploadFileName = args[++index];
                index++;
                break;
            case 'l':
                checkIfOption();
                argStruct.mode = Mode.listFiles;
                index++;
                break;
                
            //Optional arguments:    
            case 'n':
                argStruct.namesToInclude.add(args[++index]);
                index++;                
                break;  
            case 'c':
                argStruct.circleCircumference =  Integer.parseInt(args[++index]);
                
                if(argStruct.circleCircumference == -1)
                    throw new IllegalArgumentException("Expected number after: " + args[index-1]);
                
                index++;
                break;
            case 'h':
                String[] ip = args[++index].split(":", 2);
                
                if(ip.length != 2)
                    throw new IllegalArgumentException("Need host port");
                
                argStruct.hostIP = InetAddress.getByName(ip[0]);
                argStruct.hostPort = java.lang.Integer.getInteger(ip[1], 3002);
                
                index++;
                break;
                
            default:
                throw new IllegalArgumentException("Unrecognised argument: " + args[index]);
        }
        return index;
    }
}
