/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;
import java.io.IOException;
import oldtrustyclient.ArgumentParser.*;
import java.net.Socket;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.io.InputStream;
import java.util.Arrays;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Owner
 */
public class TCPClient {
    
    
    
    private Arguments argStruct;
    private Socket socket;        
    private InputStream is;
    private OutputStream os;
    
    public TCPClient(Arguments argStruct)
    {
        this.argStruct = argStruct;
        
        openSocket();
    }
    
    public void go()
    {
        switch(argStruct.mode)
        {
            case upload:
                try {
                    sendFile();
                } catch (IOException ex) {
                    System.out.printf("File upload failed\n");
                }
                break;
            case download:
        {
            try {
                downloadFile();
            } catch (IOException ex) {
                System.out.printf("File download failed\n");
            }
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
        FileOutputStream file = null;
        try {
            file = new FileOutputStream(argStruct.downloadFileName);
        } catch (FileNotFoundException ex) {
             System.out.printf("Cannot write to file\n");
        }
        
        startDownloadFile();
        
        byte[] response = readPacket();
        
        while(isOfType(response, Packet.FILE_PART))
        {
            file.write(stripHeader(response));
            writePacket(Packet.READY_TO_RECEIVE_PART.getBytes());
            response = readPacket();
        }
        
        file.close();        
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
        
        startSendFile();
        
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
    
    private void startSendFile() throws IOException
    {
        byte[] packet = addHeader(Packet.START_OF_FILE.getBytes(), argStruct.uploadFileName.getBytes(), argStruct.uploadFileName.length());
        
        writePacket(packet);
    }
    
    private void startDownloadFile() throws IOException
    {
        byte[] packet = addHeader(Packet.REQUEST_FILE.getBytes(), argStruct.downloadFileName.getBytes(), argStruct.downloadFileName.length());
        
        writePacket(packet);
        byte[] response = readPacket();
        
        if(isOfType(response    , Packet.START_OF_FILE))
            writePacket(Packet.READY_TO_RECEIVE_PART.getBytes());
        
    }
    
    private void openSocket()
    {   
        try {
            socket = new Socket(argStruct.hostIP, argStruct.hostPort);
        } catch (IOException ex) {
            System.out.printf("Could not connect to host\n");
        }   
        
        
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
