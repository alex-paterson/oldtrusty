package oldtrustyclient;

/**
 * Packet header specification
 * @author Simon de Sancha
 * @author Alex Patterson
 */
public class Packet {
    public static final String START_OF_FILE = "000";
    public static final String REQUEST_FILE  = "030";
    public static final String START_OF_CERTIFICATE = "001";
    
    public static final String FILE_PART  = "010";
    public static final String READY_TO_RECEIVE_PART  = "200";
    
    public static final String CERTIFICATE_PART  = "011";
    public static final String CERTIFICATE_ALREADY_EXISTS = "402";
    public static final String CERTIFICATE_DOESNT_EXIST = "412";
    public static final String END_OF_CERTIFICATE = "021";
    public static final String END_OF_FILE = "020";
    public static final String FILE_ALREADY_EXISTS = "401";
    public static final String FILE_DOESNT_EXIST = "411";

    public static final String REQUEST_FILE_LIST = "502";
    public static final String LIST_PACKET = "510";

    public static final String VOUCH_FOR_FILE  = "600";
    public static final String VOUCH_USING_CERT  = "612";
    public static final String READY_TO_RECEIVE_CERTIFICATE  = "611";
    public static final String FILE_SUCCESSFULLY_VOUCHED = "601";
    public static final String FILE_NOT_VOUCHED = "602";
   
    public static final String PUBKEY_CHALLENGE = "605";
    public static final String PUBKEY_RESPONSE = "606";
    public static final String PUBKEY_CHALLENGE_FAILED = "607";
    
    public static final int MAX_NAME_LENGTH = 32;
    public static final int FRAME_LENGTH = 1024;
    public static final int HEADER_LENGTH = 3;
    
}
