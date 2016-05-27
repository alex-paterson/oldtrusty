/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;
import java.io.IOException;
import oldtrustyclient.ArgParser.*;
import java.net.Socket;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.io.InputStream;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.X509Certificate;
import java.util.Arrays;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

/**
 *
 * @author Owner
 */
public class TCPClient {
    
    
    
    private ArgumentStruct argStruct;
    private SSLSocket socket;        
    private InputStream is;
    private OutputStream os;
    
    public TCPClient(ArgumentStruct argStruct) throws IOException
    {
        this.argStruct = argStruct;
        
        openSocket();
    }
    
    public void go() throws IOException
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
                    System.out.printf("File upload failed: ");
                    throw(ex);
                }
                break;
            case listFiles:
                try {
                    listFiles();
                } catch (IOException ex) {
                    System.out.printf("File upload failed: ");
                    throw(ex);
                }
                break;
            case vouch:
                try {
                    vouchFor();
                } catch (IOException ex) {
                    System.out.printf("File upload failed: ");
                    throw(ex);
                }
                break;
        }
    }
    
    private void prepareStreams()
    {
        try {
            os = socket.getOutputStream();
            is = socket.getInputStream();
        } catch (IOException ex) {
            System.out.printf("Couldn't open stream\n");
        }
    }
    
    private void downloadFile() throws IOException
    {
        if(!startDownloadFile())
            return;
        
        byte[] response = readPacket();
        
        while(isOfType(response, Packet.FILE_PART))
        {
            System.out.printf("%s", new String(stripHeader(response), java.nio.charset.StandardCharsets.UTF_8));
            writePacket(Packet.READY_TO_RECEIVE_PART.getBytes());
            response = readPacket();
        }
    }
    
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
    
    private void vouchFor() throws IOException
    {       
        FileInputStream fis = null;
        File myFile = new File(argStruct.uploadFileName);
        byte[] buf = new byte[Packet.HEADER_LENGTH + Packet.MAX_NAME_LENGTH];
        try {
            fis = new FileInputStream(myFile);
        } catch (FileNotFoundException ex) {
            System.out.printf("Could not find certificate\n");
            return;
        }
        
        buf = new byte[Packet.HEADER_LENGTH + (int)myFile.length()];
        
        BufferedInputStream bufInput = new BufferedInputStream(fis);
        int bufLength = bufInput.read(buf, 0, buf.length);
        
        
        sendPacket(Packet.VOUCH_FOR_FILE, argStruct.fileToVouch);
        byte[] response = readPacket();
        
        if(isOfType(response, Packet.READY_TO_RECEIVE_CERTIFICATE))
        {
            System.out.printf("Sending " + argStruct.uploadFileName + "(" + bufLength + " bytes)");
            
            writePacket(addHeader(Packet.VOUCH_USING_CERT.getBytes(), buf, bufLength));
            response = readPacket();
        }
        
        if(isOfType(response, Packet.FILE_SUCCESSFULLY_VOUCHED))
            System.out.printf("vouched\n");
    }
    
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
           //Error
        }
    }
    
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
    
    private boolean startDownloadFile() throws IOException
    {
        sendPacket(Packet.REQUEST_FILE,  constructDownloadPacket());
        
        byte[] response = readPacket();
        
        if(isOfType(response, Packet.START_OF_FILE))
        {
            writePacket(Packet.READY_TO_RECEIVE_PART.getBytes());
            return true;
        }
        else if(isOfType(response, Packet.FILE_NOT_VOUCHED))    
        {       
            System.out.printf("file not vouched\n");
            return false;
        }
        return false;
    }
    
    /*
    Format for requesting files:
    Header.
    1 byte circumference length
    1 byte number of names
    MAX_NAME_LENGTH bytes per name    
    MAX_NAME_LENGTH byte for filename
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
            if (argStruct.namesToInclude.length() > Packet.MAX_NAME_LENGTH) {
                System.out.printf("Name too long\n");
                return new byte[1];
            }
            System.arraycopy(argStruct.namesToInclude.getBytes(), 0, buf, i*Packet.MAX_NAME_LENGTH + 2, argStruct.namesToInclude.length());
        }
            
        if(argStruct.downloadFileName.length() > Packet.MAX_NAME_LENGTH)
        {
            System.out.printf("Filename too long\n");
            return new byte[1];
        }
            
        System.arraycopy(argStruct.downloadFileName.getBytes(), 0, buf, ifNamed*Packet.MAX_NAME_LENGTH + 2, argStruct.downloadFileName.length());
        return buf;
    }
    
    private void openSocket() throws IOException
    {   
        TrustManager[] trustAllCerts = new TrustManager[] {new X509TrustManager() {
                public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                    return null;
                }
                public void checkClientTrusted(X509Certificate[] certs, String authType) {
                }
                public void checkServerTrusted(X509Certificate[] certs, String authType) {
                }
            }
        };
        
        SSLContext sc = null;
        try {
            sc = SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new java.security.SecureRandom());
        } catch (NoSuchAlgorithmException | KeyManagementException ex) {
            System.out.printf(ex.getLocalizedMessage());
        }
        
        SSLSocketFactory f = sc.getSocketFactory();
        socket = (SSLSocket) f.createSocket(argStruct.hostIP, argStruct.hostPort);
        
        prepareStreams();
    }
    
    private boolean isOfType(byte[] packet, String header)
    {
        return java.util.Arrays.equals(Arrays.copyOf(packet, Packet.HEADER_LENGTH), header.getBytes());
    }
    
    private byte[] addHeader(byte[] header, byte[] message, int mesLength)
    {
        byte[] packet = new byte[header.length + mesLength];
        System.arraycopy(header, 0, packet, 0, header.length);
        System.arraycopy(message, 0, packet, header.length, mesLength);
        return packet;
    }
    
    private byte[] stripHeader(byte[] packet)
    {
        return Arrays.copyOfRange(packet, Packet.HEADER_LENGTH, packet.length - Packet.HEADER_LENGTH);
    }
    
    private void writePacket(byte[] packet) throws IOException
    {
        os.write(packet);
        os.flush();
    }
    
    private byte[] readPacket() throws IOException
    {
        byte[] packet = new byte[Packet.FRAME_LENGTH];
        is.read(packet);
        return packet;
    }
}
