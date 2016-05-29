package oldtrustyclient;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.List;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.impl.Arguments;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

/**
 * Processes command line arguments
 * 
 * @author Simon de Sancha
 * @author Alex Patterson
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
        
        boolean ifHostSet;
        InetAddress hostIP;
        int hostPort;
        
        String namesToInclude;
        byte circleCircumference;
        boolean ifCircleSet;
    }
    
    ArgumentStruct argStruct;
    ArgumentParser parser;
    
    public ArgParser() throws UnknownHostException
    {
        argStruct = new ArgumentStruct();
        
        //Setting defaults
        argStruct.circleCircumference = 1;
        argStruct.mode = Mode.unset;
        argStruct.ifHostSet = false;
        argStruct.ifCircleSet = false;
        argStruct.namesToInclude = null;
        
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
                .help("Name to include in circle of trust")
                .metavar("name")
                .type(String.class);
        parser.addArgument("-c")
                .help("Required length of circle of trust")
                .metavar("length")
                .type(Integer.class);
        parser.addArgument("-v")
                .help("Vouch for file on server using certificate")
                .nargs(2)
                .metavar("filename")
                .type(String.class);
        parser.addArgument("--host")
                .help("Host address and port")
                .metavar("host:port")
                .type(String.class);
    }
    
    /*
    * Checks if this situation is a valid one
    */
    private void checkIfValidArgs()
    {
        if(argStruct.mode == Mode.unset)
        {
            throw new IllegalArgumentException("Invalid argument combination");
        }
        if(!argStruct.ifHostSet)
        {
            throw new IllegalArgumentException("Need host address");
        }
        if(!argStruct.ifHostSet)
        {
            throw new IllegalArgumentException("Need host address");
        }
        if(!argStruct.ifCircleSet)
        {
            System.out.printf("Using default trust circle cirumference of %d\n", (int) argStruct.circleCircumference);
        }
    }
    
    /*
    * Attempt to parse the command line arguments
    * @param args arguments
    * @return   Argument structure
    */
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
        
        checkIfValidArgs();

        return argStruct;
    }
    
    /*
    * Process the results from the argparse4j library
    * @param res    results from argparse4j
    */
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
            @SuppressWarnings("unchecked")
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
                argStruct.namesToInclude = (String) obj;
        }
        if((obj = res.get("c")) != null)
        {
            argStruct.circleCircumference =  ((Integer) obj).byteValue();

            if (argStruct.circleCircumference < 1)
                throw new IllegalArgumentException("Illegal circumference:");
            
            argStruct.ifCircleSet = true;
        }
        
        if((obj = res.get("host")) != null)
        {
            String[] ip = ((String) obj).split(":", 2);

            if (ip.length != 2) {
                throw new IllegalArgumentException("Need host port");
            }

            argStruct.hostIP = InetAddress.getByName(ip[0]);
            argStruct.hostPort = java.lang.Integer.parseInt(ip[1]);
            
            argStruct.ifHostSet = true;
        }
    }
    
    /*
    * Check if a mutually-exclusive argument has already been specified
    */
    private void checkIfOption()
    {
        if(argStruct.mode != Mode.unset)
        {
            throw new IllegalArgumentException("Invalid argument combination");
        }        
    }
    
    public void printHelp()
    {
        parser.printHelp();
    }
}
