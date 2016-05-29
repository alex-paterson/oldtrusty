/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;
import java.io.IOException;
import oldtrustyclient.ArgParser.*;
import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.OutputStream;
import java.io.InputStream;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.security.InvalidKeyException;
import java.security.KeyFactory;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.cert.X509Certificate;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.Arrays;
import java.util.Base64;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.crypto.BadPaddingException;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;

/**
 * Communication with OldTrusty server
 * @author Simon de Sancha
 * @author Alex Patterson
 */
public class TCPClient {
    private final ArgumentStruct argStruct;
    private SSLSocket socket;        
    private InputStream is;
    private OutputStream os;
    
    /*
    * @param argStruct  command-line arguments
    */
    public TCPClient(ArgumentStruct argStruct) throws IOException
    {
        this.argStruct = argStruct;
        
        openSocket();
    }
    
    /*
    * Take action on the command-line arguments
    */
    public void go() throws IOException, ClassNotFoundException
    {
        switch(argStruct.mode)
        {
            case upload:
                try {
                    sendFile();
                } catch (IOException ex) {
                    System.out.printf("File upload failed: ");
                    throw(ex);
                }
                break;
            case download:
                try {
                    downloadFile();
                } catch (IOException ex) {
                    System.out.printf("File download failed: ");
                    throw(ex);
                }
                break;
            case uploadCertificate:
                try {
                    sendCertificate();
                } catch (IOException ex) {
                    System.out.printf("Certificate upload failed: ");
                    throw(ex);
                }
                break;
            case listFiles:
                try {
                    listFiles();
                } catch (IOException ex) {
                    System.out.printf("File list failed: ");
                    throw(ex);
                }
                break;
            case vouch:
                try {
                    vouchFor();
                } catch (IOException | NoSuchAlgorithmException | InvalidKeySpecException ex) {
                    System.out.printf("File vouch failed: ");
                }
                break;
        }
    }
    
    /*
    * Prepare netowrk IO streams
    */
    private void prepareStreams()
    {
        try {
            os = socket.getOutputStream();
            is = socket.getInputStream();
        } catch (IOException ex) {
            System.out.printf("Couldn't open stream\n");
        }
    }
    
    /*
    * Download a file specified in args
    */
    private void downloadFile() throws IOException
    {
        int length = startDownloadFile();
        if(length == -1)
            return;
        
        byte[] response = new byte[Packet.FRAME_LENGTH];
        int gotLength = is.read(response);
        
        if(isOfType(response, Packet.FILE_PART))
        {
            System.out.printf("%s\n", new String(stripHeader(response), java.nio.charset.StandardCharsets.UTF_8));
            if((gotLength-Packet.HEADER_LENGTH) != length)
            {
                System.out.printf("File corrupted\n");
            }
        }
        else
        {
            handleError(response);
        }
    }
    
    /*
    * Upload a certificate specified in args
    */
    private void sendCertificate() throws IOException
    {       
        FileInputStream fis = null;
        
        File myFile = new File(argStruct.uploadFileName);
        byte[] buf = new byte[Packet.FRAME_LENGTH];
        try {
            fis = new FileInputStream(myFile);
        } catch (FileNotFoundException ex) {
            System.out.printf("Could not find file\n");
            return;
        }
        
        BufferedInputStream bufInput = new BufferedInputStream(fis);
        
        sendPacket(Packet.START_OF_CERTIFICATE, myFile.getName());
        
        byte[] response = readPacket();
        int bufLength;
        
        while((bufLength = bufInput.read(buf, 0, buf.length)) > 0 && 
                isOfType(response, Packet.READY_TO_RECEIVE_PART))
        {
            System.out.printf("Sending " + argStruct.uploadFileName + "(" + bufLength + " bytes)");
            
            writePacket(addHeader(Packet.CERTIFICATE_PART.getBytes(), buf, bufLength));
            response = readPacket();
        }
        
        if(isOfType(response, Packet.CERTIFICATE_ALREADY_EXISTS))
            System.out.printf("Certificate already exists on server\n");
        
        sendPacket(Packet.END_OF_CERTIFICATE, "");
    }
    
    /*
    * Upload a file specified in args
    */
    private void sendFile() throws IOException
    {       
        FileInputStream fis = null;
        
        File myFile = new File(argStruct.uploadFileName);
        byte[] buf = new byte[Packet.FRAME_LENGTH];
        try {
            fis = new FileInputStream(myFile);
        } catch (FileNotFoundException ex) {
            System.out.printf("Could not find file\n");
        }
        
        BufferedInputStream bufInput = new BufferedInputStream(fis);
        
        sendPacket(Packet.START_OF_FILE, myFile.getName());
        
        byte[] response = readPacket();
        int bufLength;
        
        while((bufLength = bufInput.read(buf, 0, buf.length)) > 0 && 
                isOfType(response, Packet.READY_TO_RECEIVE_PART))
        {
            System.out.printf("Sending " + argStruct.uploadFileName + "(" + bufLength + " bytes)");
            
            writePacket(addHeader(Packet.FILE_PART.getBytes(), buf, bufLength));
            response = readPacket();
        }
        
        if(isOfType(response, Packet.FILE_ALREADY_EXISTS))
            System.out.printf("File already exists on server\n");
        
        writePacket(Packet.END_OF_FILE.getBytes());
    }
    
    /*
    * Vouch for a file specified in args
    */
    private void vouchFor() throws IOException, ClassNotFoundException, NoSuchAlgorithmException, InvalidKeySpecException
    {       
        startVouchFile(argStruct.fileToVouch, argStruct.uploadFileName);
        
        byte[] response = readPacket();
        
        if(isOfType(response, Packet.PUBKEY_CHALLENGE))
        {
            doVerification(response);
            response = readPacket();
        }
        
        if(isOfType(response, Packet.FILE_SUCCESSFULLY_VOUCHED))
        {
            System.out.printf("vouched\n");
            printPacket(response);
        }
        else
        {
            handleError(response);
        }
    }
    
    /*
    * List files on server
    */
    private void listFiles() throws IOException
    {
        sendPacket(Packet.REQUEST_FILE_LIST, "");
        
        byte[] response = readPacket();
        
        if(isOfType(response, Packet.LIST_PACKET))
        {
            String list = new String(stripHeader(response), java.nio.charset.StandardCharsets.UTF_8);
            
            System.out.printf("%s\n", list);
        }   
        else
        {
           printPacket(response);
        }
    }
    
    /*
    * Print a response from server
    * @param response   packet from server
    */
    private void printPacket(byte[] response)
    {
        System.out.printf("%s\n", new String(stripHeader(response), java.nio.charset.StandardCharsets.UTF_8));
    }
    
    /*
    * Send a packet to the server
    * @param header required header
    * @param header required data
    */
    private void sendPacket(String header, String message) throws IOException
    {
        byte[] packet = addHeader(header.getBytes(), message.getBytes(), message.length());
        
        writePacket(packet);
    }
    
    private void sendPacket(String header, byte[] message) throws IOException
    {
        byte[] packet = addHeader(header.getBytes(), message, message.length);
        
        writePacket(packet);
    }
    
    /*
    * Initiate a file vouch
    * @param filename   file to vouch for
    * @param certname   certificate to use
    */
    private void startVouchFile(String filename, String certname) throws IOException
    {
        byte[] buf = new byte[2*Packet.MAX_NAME_LENGTH];
        
        System.arraycopy(filename.getBytes(), 0, buf, 0, filename.length());
        System.arraycopy(certname.getBytes(), 0, buf, Packet.MAX_NAME_LENGTH, certname.length());
        
        sendPacket(Packet.VOUCH_FOR_FILE,  buf);
    }
    
    /*
    * Initiate a file download
    */
    private int startDownloadFile() throws IOException
    {
        sendPacket(Packet.REQUEST_FILE,  constructDownloadPacket());
        
        byte[] response = readPacket();
        
        if(isOfType(response, Packet.START_OF_FILE))
        {
            writePacket(Packet.READY_TO_RECEIVE_PART.getBytes());
            byte length[] = Arrays.copyOf(stripHeader(response), 4); //4-byte int
            return new BigInteger(length).intValue();
        }
        else if(isOfType(response, Packet.FILE_NOT_VOUCHED))    
        {       
            System.out.printf("file not vouched\n");
            return -1;
        }
        return -1;
    }
    
    /*
    * Construct the file-download header
    * @return   header
    */
    private byte[] constructDownloadPacket()
    {
        int ifNamed = 0;
        if(argStruct.namesToInclude != null)
            ifNamed = 1;
        
        byte[] buf = new byte[2 + ifNamed*Packet.MAX_NAME_LENGTH + Packet.MAX_NAME_LENGTH];
        buf[0] = argStruct.circleCircumference;
        buf[1] = (byte) ifNamed;
        for(int i = 0; i < ifNamed; i++)
        {
            System.arraycopy(bufferString(argStruct.namesToInclude), 0, buf, i*Packet.MAX_NAME_LENGTH + 2, Packet.MAX_NAME_LENGTH);
        }
            
        System.arraycopy(bufferString(argStruct.downloadFileName), 0, buf, ifNamed*Packet.MAX_NAME_LENGTH + 2, Packet.MAX_NAME_LENGTH);
        return buf;
    }
    
    /*
    * Buffer a string up to required length
    * @param s  string to buffer
    * @return   buffered string
    */
    private byte[] bufferString(String s)
    {
        if(s.length() > Packet.MAX_NAME_LENGTH)
        {
            System.out.printf("Name too long\n");
            return new byte[Packet.MAX_NAME_LENGTH];
        }
        byte[] buf = new byte[Packet.MAX_NAME_LENGTH];
        System.arraycopy(s.getBytes(), 0, buf, 0, s.length());
        return buf;
    }
    
    /*
    * Open an SSL socket to the server
    */
    private void openSocket() throws IOException
    {   
        File server = new File("trust.jks");
        if(!server.exists())
        {
            System.out.printf("Cannot find server certificate\n");
            throw new IOException("No server certificate");
        }
        
        
        System.setProperty("javax.net.ssl.trustStore", "trust.jks");
        SSLSocketFactory f = (SSLSocketFactory) SSLSocketFactory.getDefault();
        
        socket = (SSLSocket) f.createSocket(argStruct.hostIP, argStruct.hostPort);
        
        prepareStreams();
    }
    
    /*
    * Handle an unexpected packet from server
    * @param  response  packet from server
    */
    private void handleError(byte[] response)
    {
        printPacket(response);
        if(isOfType(response, Packet.CERTIFICATE_DOESNT_EXIST)) {
            System.out.printf("Certificate doesn't exist\n");
        } else if(isOfType(response, Packet.FILE_DOESNT_EXIST)) {
            System.out.printf("File doesn't exist\n");
        }
    }
    
    /*
    * Checks if packet is of type
    * @param packet     specified packet
    * @param header     header to check for
    * @return   result
    */
    private boolean isOfType(byte[] packet, String header)
    {
        return java.util.Arrays.equals(Arrays.copyOf(packet, Packet.HEADER_LENGTH), header.getBytes());
    }
    
    /*
    * Prefixes a header to a data packet
    * @param packet     specified packet
    * @param message    data
    * @param mesLength  length of data
    * @return           finished packet
    */
    private byte[] addHeader(byte[] header, byte[] message, int mesLength)
    {
        byte[] packet = new byte[header.length + mesLength];
        System.arraycopy(header, 0, packet, 0, header.length);
        System.arraycopy(message, 0, packet, header.length, mesLength);
        return packet;
    }
    
    /*
    * Strips packet down to data portion
    * @param packet     packet
    * @return       data portion of packet
    */
    private byte[] stripHeader(byte[] packet)
    {
        return Arrays.copyOfRange(packet, Packet.HEADER_LENGTH, packet.length - Packet.HEADER_LENGTH);
    }
    
    /*
    * Sends packet to server
    * @param packet     packet
    */
    private void writePacket(byte[] packet) throws IOException
    {
        os.write(packet);
        os.flush();
    }
    
    /*
    * Reads packet from server (blocking)
    * @return   packet
    */
    private byte[] readPacket() throws IOException
    {
        byte[] packet = new byte[Packet.FRAME_LENGTH];
        is.read(packet);
        return packet;
    }
    
    /*
    * Complete a random-number challenge from server
    * @param packet     packet
    */
    private void doVerification(byte[] response) throws IOException, ClassNotFoundException, NoSuchAlgorithmException, InvalidKeySpecException
    {
        byte[] data = Arrays.copyOf(stripHeader(response), 172);
        byte[] decoded = Base64.getDecoder().decode(data);
        byte[] realData = doDataEncryption(decoded, false);
        
        int number = Integer.parseInt(new String(realData));
        number = number + 499;
        
        byte[] num = ByteBuffer.allocate(4).putInt(number).array();
        byte[] encoded = doDataEncryption(num, true);
        realData = Base64.getEncoder().encode(encoded);
        
        sendPacket(Packet.PUBKEY_RESPONSE, realData);
    }
    
    /*
    * Encrypts/decrypts data using RSA
    * @param data   data
    * @param ifEncrypt  if encrypting or decrypting
    * @return   finished data
    */
    private byte[] doDataEncryption(byte[] data, boolean ifEncrypt) throws IOException, ClassNotFoundException, NoSuchAlgorithmException, InvalidKeySpecException
    {
        Cipher cipher = null;
        try {
            cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
        } catch (NoSuchAlgorithmException | NoSuchPaddingException ex) {
            System.out.printf("Error in encryption: %s\n", ex.getLocalizedMessage());
            return new byte[2];
        }
        PrivateKey privKey = loadPrivateKey();
        try {
            cipher.init(ifEncrypt ? Cipher.ENCRYPT_MODE : Cipher.DECRYPT_MODE, privKey);
        } catch (InvalidKeyException ex) {
            Logger.getLogger(TCPClient.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        try {
            return cipher.doFinal(data);
        } catch (IllegalBlockSizeException | BadPaddingException ex) {
            System.out.printf("Error in encryption: %s\n", ex.getLocalizedMessage());
        }
        return new byte[2];
    }
    
    /*
    * Load private key from file
    * @return   private key object
    */
    private PrivateKey loadPrivateKey() throws IOException, ClassNotFoundException, NoSuchAlgorithmException, InvalidKeySpecException
    {
        File f = new File("client.der");
        if(!f.exists())
        {
            System.out.printf("Cannot find client private key\n");
            throw new IOException("No client key");
        }
        
        FileInputStream fis = new FileInputStream(f);
        DataInputStream dis = new DataInputStream(fis);
        byte[] keyBytes = new byte[(int) f.length()];
        dis.readFully(keyBytes);
        dis.close();

        PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(keyBytes);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        return kf.generatePrivate(spec);
    }
    
    
    
}
