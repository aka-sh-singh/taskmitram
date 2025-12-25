import ChatSidebar from '@/components/chat/ChatSidebar';
import ChatWindow from '@/components/chat/ChatWindow';

const Chat = () => {
    return (
        <div className="flex h-screen overflow-hidden">
            <ChatSidebar />
            <ChatWindow />
        </div>
    );
};

export default Chat;
