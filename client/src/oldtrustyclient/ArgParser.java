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
import java.util.Map;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.impl.Arguments;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

/**
 *
 * @author Owner
 */
public class ArgParser {
    
    public enum Mode {
        unset,
        upload,
        download,
        vouch,
        listFiles,
        uploadCertificate;
       };
    
    public class ArgumentStruct {
        Mode mode;
        
        String uploadFileName;
        String downloadFileName;
        String fileToVouch;
        
        InetAddress hostIP;
        int hostPort;
        
        List<String> namesToInclude;
        byte circleCircumference;
    }
    
    ArgumentStruct argStruct;
    ArgumentParser parser;
    
    public ArgParser() throws UnknownHostException
    {
        argStruct = new ArgumentStruct();
        
        //Setting defaults
        argStruct.circleCircumference = 1;
        argStruct.mode = Mode.unset;
        //argStruct.hostIP = InetAddress.getByName("192.168.0.132");
       // argStruct.hostPort = 3002;
        
        argStruct.namesToInclude = new ArrayList<>();
        
        parser = ArgumentParsers.newArgumentParser("oldTrustyClient")
                .description("Client interface to oldTrusty program.");
        parser.addArgument("-a")
                .help("Upload file")
                .metavar("file")
                .type(String.class);
        parser.addArgument("-f")
                .help("Download file from server")
                .metavar("file")
                .type(String.class);
        parser.addArgument("-u")
                .help("Upload certificate to server")
                .metavar("certificate")
                .type(String.class);
        parser.addArgument("-l")
                .action(Arguments.storeTrue())
                .help("List files on server");
        parser.addArgument("-n")
                .help("Names to include in circle of trust")
                .metavar("name ...")
                .type(String.class);
        parser.addArgument("-c")
                .help("Required length of circle of trust")
                .metavar("length")
                .type(Integer.class);
        parser.addArgument("-v")
                .help("Vouch for file on server using certificate")
                .nargs(2)
                .metavar("file certificate")
                .type(String.class);
        parser.addArgument("--host")
                .help("Host address and port")
                .metavar("host:port")
                .type(String.class);
    }
    
    public ArgumentStruct parse(String[] args) throws UnknownHostException, ArgumentParserException
    {
        Namespace res;

        try {
            res = parser.parseArgs(args);
            fillStruct(res);
        } catch (ArgumentParserException e) {
            parser.handleError(e);
            System.exit(1);
        }

        return argStruct;
    }
    
    private void fillStruct(Namespace res) throws UnknownHostException
    {
        Object obj;
        if((obj = res.get("a")) != null)
        {
            checkIfOption();
            argStruct.mode = Mode.upload;
            argStruct.uploadFileName = (String) obj;
        } 
        if((obj = res.get("f")) != null)
        {
            checkIfOption();
            argStruct.mode = Mode.download;
            argStruct.downloadFileName = (String) obj;
        }
        if((obj = res.get("u")) != null)
        {
            checkIfOption();
            argStruct.mode = Mode.uploadCertificate;
            argStruct.uploadFileName = (String) obj;
        }
        if((obj = res.get("v")) != null)
        {
            List<String> list = (List<String>) obj;
            checkIfOption();
            argStruct.mode = Mode.vouch;
            argStruct.fileToVouch = list.get(0);
            argStruct.uploadFileName = list.get(1);
        }
        if((boolean) res.get("l") == true)
        {
            checkIfOption();
            argStruct.mode = Mode.listFiles;
        }
        if((obj = res.get("n")) != null)
        {
                argStruct.namesToInclude.add((String)obj);
        }
        if((obj = res.get("c")) != null)
        {
            argStruct.circleCircumference =  ((Integer) obj).byteValue();

            if (argStruct.circleCircumference < 1)
                throw new IllegalArgumentException("Illegal circumference:");
        }
        
        if((obj = res.get("host")) != null)
        {
            String[] ip = ((String) obj).split(":", 2);

            if (ip.length != 2) {
                throw new IllegalArgumentException("Need host port");
            }

            argStruct.hostIP = InetAddress.getByName(ip[0]);
            argStruct.hostPort = java.lang.Integer.getInteger(ip[1], 3002);
        }
    }
    
    private void checkIfOption()
    {
        if(argStruct.mode != Mode.unset)
        {
            throw new IllegalArgumentException("Invalid argument combination");
        }        
    }
}
