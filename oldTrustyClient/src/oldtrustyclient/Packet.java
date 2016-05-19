/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package oldtrustyclient;

/**
 *
 * @author Owner
 */
public class Packet {
    public static final String START_OF_FILE = "000";
    public static final String REQUEST_FILE  = "030";
    public static final String START_OF_CERTIFICATE = "001";
    public static final String FILE_PART  = "010";
    public static final String READY_TO_RECEIVE_PART  = "200";
    
    public static final String CERTIFICATE_PART  = "011";
    public static final String CERTIFICATE_ALREADY_EXISTS  = "402";
    public static final String END_OF_CERTIFICATE  = "021";
    public static final String END_OF_FILE  = "020";
    public static final String FILE_ALREADY_EXISTS  = "401";
    
    public static final String REQUEST_FILE_LIST  = "502";
    public static final String LIST_PACKET  = "510";
    
    public static final int FRAME_LENGTH = 1024;
    public static final int HEADER_LENGTH = 3;
    
    
    
    
    
/*public static final StringEND_OF_CERTIFICATE  = '021' 
public static final String    FILE_DOESNT_EXIST  = '411' 
public static final String   CERTIFICATE_ALREADY_EXISTS  = '402
public static final String  CERTIFICATE_DOESNT_EXIST  = "412" ;
public static final StringUNRECOGNIZED_HEADER  = '500" 
public static final String UNEXPECTED_HEADER  = '501"*/
}
